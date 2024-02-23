from girder.exceptions import ValidationException
from girder.utility.abstract_assetstore_adapter import AbstractAssetstoreAdapter
from girder_client import GirderClient, AuthenticationError
from girder.models.file import File
from girder.models.folder import Folder
from girder.models.item import Item

GIRDER_ASSETSTORE_META_KEY = 'girder_assetstore_meta'


class GirderAssetstoreAdapter(AbstractAssetstoreAdapter):
    """
    Assetstore adapter for external girder assetstores
    """

    def __init__(self, assetstore):
        super().__init__(assetstore)
        # TODO: add better checking for doc parameters
        if 'url' in self.assetstore_meta:
            self.client = GirderClient(host=self.assetstore_meta['url'])

    @property
    def assetstore_meta(self):
        return self.assetstore[GIRDER_ASSETSTORE_META_KEY]

    @staticmethod
    def validateInfo(doc):
        meta = doc.get(GIRDER_ASSETSTORE_META_KEY, {})

        # TODO: remove this assumption (?)
        # ensure that the assetstore is marked read-only
        doc['readOnly'] = True

        if 'url' not in meta:
            raise ValidationException(f'Must specify a "url" for remote Girder assetstore')

        convert_empty_fields_to_none = [
            'username',
            'password',
            'prefix',
        ]

        for field in convert_empty_fields_to_none:
            if isinstance(meta.get(field), str) and not meta[field].strip():
                meta[field] = None

        # verify that we can connect to the server
        client = GirderClient(host=meta['url'])
        try:
            user = client.authenticate(username=meta['username'], password=meta['password'])
            # TODO: add check for prefix existence
        except:
            raise ValidationException('Failed to authenticate with the remote Girder server')

        doc[GIRDER_ASSETSTORE_META_KEY] = meta
        return doc

    def initUpload(self, upload):
        raise NotImplementedError('Girder assetstores are import only.')

    def finalizeUpload(self, upload, file):
        raise NotImplementedError('Girder assetstores are import only.')

    def getFileSize(self, file):
        return

    def deleteFile(self, file):
        # we don't actually need to do anything special
        return

    def downloadFile(self, file, offset=0, headers=True, endByte=None,
                     contentDisposition=None, extraParameters=None, **kwargs):

        return

    def setContentHeaders(self, file, offset, endByte, contentDisposition=None):
        """
        Sets the Content-Length, Content-Disposition, Content-Type, and also
        the Content-Range header if this is a partial download.

        :param file: The file being downloaded.
        :param offset: The start byte of the download.
        :type offset: int
        :param endByte: The end byte of the download (non-inclusive).
        :type endByte: int or None
        :param contentDisposition: Content-Disposition response header
            disposition-type value, if None, Content-Disposition will
            be set to 'attachment; filename=$filename'.
        :type contentDisposition: str or None
        """
        return


    def _importData(self, parent, parentType, src_path, params, progress, user):
        progress.update(message=f'Importing {src_path}')

        # get source metadata
        src_meta = self.client.get('resource/lookup', parameters={'path': src_path})
        src_type = src_meta['_modelType']
        src_id = src_meta['_id']

        # TODO: make this more general
        if src_type != 'folder':
            raise Exception('Only folders can be imported (currently)')

        folders = []
        # create subfolders
        for src_folder in self.client.listFolder(parentId=src_id, parentFolderType=src_type):
            if self.shouldImportFile(f"{src_path}/{src_item['name']}", params):
                folders.append(
                    Folder().createFolder(
                        parent=parent,
                        name=src_folder['name'],
                        creator=user,
                        reuseExisting=True
                    )
                )

        items = []
        # create copies of items in current folder
        for src_item in self.client.listItem(folderId=src_id):
            if self.shouldImportFile(f"{src_path}/{src_item['name']}", params):
                progress.update(message=src_item['name'])

                item = Item().createItem(
                    name=src_item['name'],
                    creator=user,
                    folder=parent,
                    reuseExisting=True
                )

                file = File().createFile(
                    item=item,
                    creator=user,
                    name=src_item['name'],
                    size=src_item['size'],
                    assetstore=self.assetstore,
                    reuseExisting=True,
                    saveFile=False
                )
                file['girderRemoteSource'] = src_item['_id']
                file['imported'] = True
                file = File().save(file)

        # recurse into subfolders
        for folder in folders:
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
        self.client.authenticate(username=self.assetstore_meta['username'], password=self.assetstore_meta['password'])

        base_path = params.get('importPath')
        base_path = f'/{self.assetstore_meta["prefix"]}/{base_path}'.strip('/')

        # src_type = params.get('resourceType', 'user') # get the resource type ('collection' or 'user')
        # TODO: ensure that self.assetstore_meta['prefix'] contains /collection/... or /user/...
        #       also make sure to remove trailing '/' from the prefix
        #       do this in validateInfo()

        self._importData(parent, parentType, base_path, params, progress, user)
