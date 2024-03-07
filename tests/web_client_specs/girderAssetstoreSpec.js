// These will be replaced by templating
const url = GIRDER_ASSETSTORE_TEST_URL;
const token = GIRDER_ASSETSTORE_TEST_TOKEN;

girderTest.importPlugin('girder_assetstore');

girderTest.startApp();

describe('Girder assetstore', function () {
    // maybe see how this is done in other tests -- it may not be necessary
    it('register a user (admin)',
        girderTest.createUser('admin',
            'admin@girder.test',
            'Admin',
            'Admin',
            'adminpassword!'));

    it('Create an assetstore and import data', function () {
        runs(function () {
            $('a.g-nav-link[g-target="admin"]').trigger('click');
        });

        waitsFor(function () {
            return $('.g-assetstore-config:visible').length > 0;
        }, 'navigate to admin page');

        runs(function () {
            $('a.g-assetstore-config').trigger('click');
        });

        waitsFor(function () {
            return $('#g-create-gas-tab').length > 0;
        }, 'wait for creation tab to be loaded');
        runs(function () {
            expect($('#g-create-gas-tab').length);
        });

        // Create new Girder assetstore
        runs(function () {
            $('.panel-heading[data-target="#g-create-gas-tab"]').trigger('click');
        });

        waitsFor(function () {
            return $('#g-create-gas-tab:visible').length > 0;
        }, 'open create girder assetstore form');

        // populate form
        runs(function () {
            $('#g-new-gas-name').val('Girder Assetstore');
            $('#g-new-gas-url').val(url);
            $('#g-new-gas-path-prefix').val('/user/admin/Public');

            $('#g-new-gas-api-key').val('');
            $('#g-new-gas-username').val('');
            $('#g-new-gas-password').val('');
        });

        runs(function () {
            $('#g-new-gas-form input[type="submit"]').trigger('click');
        });

        waitsFor(function () {
            return $('#g-new-gas-error').html().length > 0;
        }, 'wait for error message to appear');

        runs(function () {
            const expected = 'Must specify either "apiKey" or "username" and "password"';
            expect($('#g-new-gas-error').html()).toBe(expected);
            $('#g-new-gas-error').html(''); // reset
        });

        // TODO: add test cases for other bad form permuations
        // TODO: add test case for API key auth (valid)
        // TODO: add test case for user/pass auth (valid)
    });
});
