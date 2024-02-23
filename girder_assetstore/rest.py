from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource
from girder.constants import TokenScope
from girder.models.assetstore import Assetstore
from girder.utility import assetstore_utilities
from girder.utility.model_importer import ModelImporter
from girder.utility.progress import ProgressContext


class GirderAssetstoreResource(Resource):
    def __init__(self):
        super().__init__()
        self.resourceName = 'girder_assetstore'
        self.route('POST', (':id', 'import'), self.importData)

    @access.admin(scope=TokenScope.DATA_WRITE)
    @autoDescribeRoute(
        Description('Import data from a remote GirderAssetstore instance')
        .modelParam('id', model=Assetstore)
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
    def importData(self, assetstore, destinationId, destinationType, progress):
        user = self.getCurrentUser()
        adapter = assetstore_utilities.getAssetstoreAdapter(assetstore)

        if destinationType != 'folder':
            raise Exception(
                'Only folder destinations are supported currently. TODO: make this more general')
        parent = ModelImporter.model(destinationType).load(destinationId, force=True, exc=True)

        with ProgressContext(progress, user=user, title='Importing data') as ctx:
            adapter.importData(parent, destinationType, params={}, progress=ctx, user=user)
