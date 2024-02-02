from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource
from girder.constants import TokenScope
from girder.models.assetstore import Assetstore

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
        # TODO: add implementation
        return None
