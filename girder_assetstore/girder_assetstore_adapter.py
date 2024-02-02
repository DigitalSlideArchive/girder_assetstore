from girder.exceptions import ValidationException
from girder.utility.abstract_assetstore_adapter import AbstractAssetstoreAdapter
from girder_client import GirderClient, AuthenticationError

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

    def importData(self, parent, parentType, params, progress, user, **kwargs):
        """
        Import Girder instances from a remote Girder server.

        :param parent: The parent object to import into.
        :param parentType: The model type of the parent object.
        :type parentType: str
        :param params: Additional parameters required for the import process.
        :type params: dict
        :param progress: Object on which to record progress if possible.
        :type progress: :py:class:`girder.utility.progress.ProgressContext`
        :param user: The Girder user performing the import.
        :type user: dict or None
        :return: a list of items that were created
        """
        return
