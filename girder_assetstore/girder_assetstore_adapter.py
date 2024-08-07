import collections
import functools

from girder import logger
from girder.api.rest import setResponseHeader
from girder.exceptions import ValidationException
from girder.models.file import File
from girder.models.folder import Folder
from girder.models.item import Item
from girder.utility.abstract_assetstore_adapter import AbstractAssetstoreAdapter
from girder_client import GirderClient, HttpError

BUF_SIZE = 65536

GIRDER_ASSETSTORE_META_KEY = 'girder_assetstore_meta'


# provide caching for authenticated GirderClient instances
@functools.lru_cache()
def _get_girder_client(assetstore_meta):
    meta = assetstore_meta._asdict()
    if 'url' in meta:
        client = GirderClient(apiUrl=meta['url'])
        if meta.get('apiKey'):
            client.authenticate(apiKey=meta['apiKey'])
        elif meta.get('username') and meta.get('password'):
            client.authenticate(username=meta['username'], password=meta['password'])
        return client
    return None


def _meta_to_serial(meta):
    # convert GirderAssetstoreAdapter metadata to a serializable form
    SerialMeta = collections.namedtuple('SerialMeta', sorted(meta.keys()))
    return SerialMeta(**meta)


class GirderAssetstoreAdapter(AbstractAssetstoreAdapter):
    """
    Assetstore adapter for external Girder assetstores.

    Connect using remote Girder API url, username, and password.
    Specify a path prefix to set the root path of the remote assetstore.
    """

    def __init__(self, assetstore):
        super().__init__(assetstore)

    @property
    def assetstore_meta(self):
        return self.assetstore[GIRDER_ASSETSTORE_META_KEY]

    @property
    def client(self):
        try:
            return _get_girder_client(_meta_to_serial(self.assetstore_meta))
        except Exception as e:
            logger.exception(f'Unable to connect to remote Girder client: {e}')
            return None

    @staticmethod
    def validateInfo(doc):
        meta = doc.get(GIRDER_ASSETSTORE_META_KEY, {})

        # TODO: remove this assumption (?)
        # ensure that the assetstore is marked read-only
        doc['readOnly'] = True

        if 'url' not in meta:
            raise ValidationException('Must specify a "url" for remote Girder assetstore')

        try:
            # verify that we can connect to the server
            client = _get_girder_client(_meta_to_serial(meta))
        except Exception as e:
            raise ValidationException(f'Failed to authenticate with the remote Girder server: {e}')

        if client is None:
            raise ValidationException('Failed to authenticate with the remote Girder server')

        doc[GIRDER_ASSETSTORE_META_KEY] = meta
        return doc

    def initUpload(self, upload):
        raise NotImplementedError('Girder assetstores are import only.')

    def finalizeUpload(self, upload, file):
        raise NotImplementedError('Girder assetstores are import only.')

    def deleteFile(self, file):
        # we don't actually need to do anything special
        return

    def downloadFile(self, file, offset=0, headers=True, endByte=None,
                     contentDisposition=None, extraParameters=None, **kwargs):
        if self.client is None:
            logger.error('Failed to connect to remote Girder server')
            raise ValidationException('Failed to connect to remote Girder server')

        if endByte is None or endByte > file['size']:
            endByte = file['size']

        if headers:
            setResponseHeader('Accept-Ranges', 'bytes')
            self.setContentHeaders(file, offset, endByte, contentDisposition)

        params = {
            'offset': offset,
            'endByte': endByte,
            'contentDisposition': contentDisposition,
            'extraParameters': extraParameters
        }
        params = {key: val for key, val in params.items() if val is not None}

        src_file_id = file['girderRemoteSourceFile']

        req = self.client.sendRestRequest(
            'get',
            f'file/{src_file_id}/download',
            stream=True,
            jsonResp=False,
            parameters=params)

        def stream():
            for chunk in req.iter_content(chunk_size=BUF_SIZE):
                yield chunk

        return stream

    def _importData(self, parent, parentType, src_path, params, progress, user):
        progress.update(message=f'Importing {src_path}')

        try:
            # get source metadata
            src_meta = self.client.get('resource/lookup', parameters={'path': src_path})
        except HttpError as e:
            raise ValidationException(
                f'Could not resolve path {src_path} on remote Girder server: "{e.response.text}"')

        src_type = src_meta['_modelType']
        src_id = src_meta['_id']

        # if the src_type is a folder, import items and files
        # if src_type in ('collection', 'user'), there are no items/files to import
        if src_type == 'folder':
            for src_item in self.client.listItem(folderId=src_id):
                if self.shouldImportFile(f"{src_path}/{src_item['name']}", params):
                    progress.update(message=src_item['name'])

                    src_item_description = src_item.get('description', '')
                    src_item_meta = src_item.get('meta', {})

                    item = Item().createItem(
                        name=src_item['name'],
                        description=src_item_description,
                        creator=user,
                        folder=parent,
                        reuseExisting=True
                    )
                    item['girderRemoteSourceItem'] = src_item['_id']
                    Item().setMetadata(item, src_item_meta)
                    item = Item().save(item)

                    # create new records for all files attached to src_item
                    for src_file in self.client.listFile(itemId=src_item['_id']):
                        file = File().createFile(
                            item=item,
                            creator=user,
                            name=src_file['name'],
                            size=src_file['size'],
                            assetstore=self.assetstore,
                            reuseExisting=True,
                            saveFile=False
                        )
                        file['girderRemoteSourceFile'] = src_file['_id']
                        file['imported'] = True
                        file = File().save(file)

        # import subfolders
        for src_folder in self.client.listFolder(parentId=src_id, parentFolderType=src_type):
            if self.shouldImportFile(f"{src_path}/{src_folder['name']}", params):
                progress.update(message=src_folder['name'])

                src_folder_description = src_folder.get('description', '')
                src_folder_meta = src_folder.get('meta', {})

                folder = Folder().createFolder(
                    parent=parent,
                    name=src_folder['name'],
                    description=src_folder_description,
                    creator=user,
                    reuseExisting=True
                )
                Folder().setMetadata(folder, src_folder_meta)
                folder = Folder().save(folder)

                # recurse into subfolder
                next_path = f'{src_path}/{folder["name"]}'
                self._importData(folder, 'folder', next_path, params, progress, user)

    def importData(self, parent, parentType, params, progress, user, **kwargs):
        """
        Import Girder data from a remote Girder server.

        :param parent: The parent object to import into.
        :param parentType: The model type of the parent object.
        :type parentType: str
        :param params: Additional parameters required for the import process.
        :type params: dict
        :param progress: Object on which to record progress if possible.
        :type progress: :py:class:`girder.utility.progress.ProgressContext`
        :param user: The Girder user performing the import.
        :type user: dict or None
        """
        if self.client is None:
            raise ValidationException('Failed to connect to remote Girder server')

        base_path = params.get('importPath')
        base_path = f'{self.assetstore_meta["prefix"]}/{base_path}'.rstrip('/')

        # TODO: add check that base_path is valid

        self._importData(parent, parentType, base_path, params, progress, user)
