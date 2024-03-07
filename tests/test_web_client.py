import os
import sys
import tempfile

import pytest

# We support Python 3.9 and greater for DICOMweb
pytestmark = [
    pytest.mark.skipif(sys.version_info < (3, 9), reason='requires python3.9 or higher'),
    pytest.mark.skipif(os.getenv('GIRDER_ASSETSTORE_TEST_URL') is None,
                       reason='GIRDER_ASSETSTORE_TEST_URL is not set'),
]


@pytest.mark.girder()
@pytest.mark.girder_client()
@pytest.mark.plugin('girder_assetstore')
def testGirderAssetstoreClient(boundServer, fsAssetstore, db):
    from pytest_girder.web_client import runWebClientTest

    spec = os.path.join(os.path.dirname(__file__), 'web_client_specs', 'girderAssetstoreSpec.js')

    # Replace the template variables
    with open(spec) as rf:
        data = rf.read()

    # girder_assetstore_test_url = os.environ['GIRDER_ASSETSTORE_TEST_URL']
    girder_assetstore_test_url = 'https://data.kitware.com/api/v1'
    data = data.replace('GIRDER_ASSETSTORE_TEST_URL', f"'{girder_assetstore_test_url}'")

    girder_assetstore_test_token = os.getenv('GIRDER_ASSETSTORE_TEST_TOKEN')
    if girder_assetstore_test_token:
        girder_assetstore_test_token = f"'{girder_assetstore_test_token}'"
    else:
        girder_assetstore_test_token = 'null'
    data = data.replace('GIRDER_ASSETSTORE_TEST_TOKEN', girder_assetstore_test_token)

    # Need to avoid context manager for this to work on Windows
    tf = tempfile.NamedTemporaryFile(delete=False)
    try:
        tf.write(data.encode())
        tf.close()
        runWebClientTest(boundServer, tf.name, 15000)
    finally:
        os.remove(tf.name)
