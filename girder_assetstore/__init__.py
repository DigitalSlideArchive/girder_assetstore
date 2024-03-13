from girder import events, plugin
from girder.api.v1.assetstore import Assetstore as AssetstoreResource
from girder.constants import AssetstoreType
from girder.models.assetstore import Assetstore
from girder.utility.assetstore_utilities import setAssetstoreAdapter

from .girder_assetstore_adapter import GIRDER_ASSETSTORE_META_KEY, GirderAssetstoreAdapter
from .rest import GirderAssetstoreResource


def createAssetstore(event):
    """
    Store the GirderAssetstore information in the database.

    :param event: Girder rest.post.assetstore.before event.
    """
    params = event.info['params']

    if params.get('type') == AssetstoreType.GIRDER:
        event.addResponse(Assetstore().save({
            'type': AssetstoreType.GIRDER,
            'name': params.get('name'),
            GIRDER_ASSETSTORE_META_KEY: {
                'url': params['url'],
                'prefix': params.get('prefix'),
                'apiKey': params.get('apiKey'),
                'username': params.get('username'),
                'password': params.get('password'),
            },
        }))
        event.preventDefault()


def updateAssetstore(event):
    """
    Update the GirderAssetstore information in the database.

    :param event: Girder assetstore.update event.
    """
    params = event.info['params']
    store = event.info['assetstore']

    if store['type'] == AssetstoreType.GIRDER:
        store[GIRDER_ASSETSTORE_META_KEY] = {
            'url': params['url'],
            'prefix': params.get('prefix'),
            'apiKey': params.get('apiKey'),
            'username': params.get('username'),
            'password': params.get('password'),
        }


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'girder_assetstore'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        plugin.getPlugin('jobs').load(info)

        # load the assetstore adapter and resource
        AssetstoreType.GIRDER = 'girder'
        setAssetstoreAdapter(AssetstoreType.GIRDER, GirderAssetstoreAdapter)
        events.bind('assetstore.update', 'girder_assetstore', updateAssetstore)
        events.bind('rest.post.assetstore.before', 'girder_assetstore', createAssetstore)

        (AssetstoreResource.createAssetstore.description
            .param('url', 'The base URL for the remote Girder server', required=True)
            .param('prefix', 'The path prefix to use for all requests', required=False)
            .param('apiKey', 'A Girder API Key used for authentication', required=False)
            .param('username', 'A Girder username useed for authentication', required=False)
            .param('password', 'A Girder password useed for authentication', required=False))

        info['apiRoot'].girder_assetstore = GirderAssetstoreResource()
