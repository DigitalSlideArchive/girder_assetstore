from girder.api import access, filter_logging
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource
from girder.constants import TokenScope
from girder.models.assetstore import Assetstore
from girder.utility import assetstore_utilities
from girder.utility.model_importer import ModelImporter
from girder.utility.progress import ProgressContext

from .girder_assetstore_adapter import GirderAssetstoreAdapter


class GirderAssetstoreResource(Resource):
    def __init__(self):
        super().__init__()
        self.resourceName = 'girder_assetstore'
        self.route('POST', (':id', 'import'), self.importData)

        filter_logging.addLoggingFilter(
            'GET (/[^/ ?#]+)*/file/[^/ ?#]+/download\\?offset',
            frequency=250, duration=10)

    @access.admin(scope=TokenScope.DATA_WRITE)
    @autoDescribeRoute(
        Description('Import data from a remote GirderAssetstore instance')
        .modelParam('id', 'The ID of the Girder Assetstore.', model=Assetstore)
        .param('importPath', 'Path to the data to import on the remote server.'
               'This is a path relative to the path prefix of the assetstore.',)
        .param('destinationId', 'The ID of the parent folder, collection, or user '
               'in the Girder data hierarchy under which to import the files.')
        .param('destinationType', 'The type of the parent object to import into.',
               enum=('folder', 'user', 'collection'),
               required=False, default='folder')
        .param('progress', 'Whether to record progress on this operation.',
               required=False, default=False, dataType='boolean')
        .errorResponse()
        .errorResponse('You are not an administrator.', 403),
    )
    def importData(self, assetstore, importPath, destinationId, destinationType, progress):
        user = self.getCurrentUser()

        if destinationType != 'folder':
            raise Exception(
                'Only folder destinations are supported currently. TODO: make this more general')
        parent = ModelImporter.model(destinationType).load(destinationId, force=True, exc=True)

        with ProgressContext(progress, user=user, title='Importing data') as ctx:
            GirderAssetstoreAdapter(assetstore).importData(
                parent,
                destinationType,
                params={
                    'importPath': importPath
                },
                progress=ctx,
                user=user)
