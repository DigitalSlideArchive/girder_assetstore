from girder.exceptions import ValidationException
from girder.utility.abstract_assetstore_adapter import AbstractAssetstoreAdapter

GIRDER_ASSETSTORE_META_KEY = 'girder_assetstore_meta'


class GirderAssetstoreAdapter(AbstractAssetstoreAdapter):
    """
    Assetstore adapter for external girder assetstores
    """

    def __init__(self, assetstore):
        super().__init__(assetstore)

    @staticmethod
    def validateInfo(doc):
        # Ensure that the assetstore is marked read-only
        doc['readOnly'] = True

        required_fields = [
            'url',
        ]

        info = doc.get(GIRDER_ASSETSTORE_META_KEY, {})

        for field in required_fields:
            if field not in info:
                raise ValidationException(f'Missing field {field}')

        convert_empty_fields_to_none = [
            'username',
            'password',
            'path_prefix',
        ]

        for field in convert_empty_fields_to_none:
            if isinstance(info.get(field), str) and not info[field].strip():
                info[field] = None

        # Verify that we can connect to the server
        # TODO: add this validation

        return doc

    def initUpload(self, upload):
        raise NotImplementedError('Girder assetstores are import only.')

    def finalizeUpload(self, upload, file):
        raise NotImplementedError('Girder assetstores are import only.')

    def getFileSize(self, file):
        return

    def deleteFile(self, file):
        # We don't actually need to do anything special
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
