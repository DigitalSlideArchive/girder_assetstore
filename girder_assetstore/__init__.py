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
                'username': params.get('username'),
                'password': params.get('password'),
                'prefix': params.get('prefix'),
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
            'username': params.get('username'),
            'password': params.get('password'),
            'prefix': params.get('prefix'),
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
            .param('username', 'The username to use for authentication', required=True)
            .param('password', 'The password to use for authentication', required=True)
            .param('prefix', 'The path prefix to use for all requests', required=True))

        info['apiRoot'].girder_assetstore = GirderAssetstoreResource()
