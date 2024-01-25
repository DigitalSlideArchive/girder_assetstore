import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('girder_assetstore')
def test_import(server):
    assert 'girder_assetstore' in loadedPlugins()
