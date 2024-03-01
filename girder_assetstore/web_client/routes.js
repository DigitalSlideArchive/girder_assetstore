import router from '@girder/core/router';
import events from '@girder/core/events';
import AssetstoreModel from '@girder/core/models/AssetstoreModel';

import GirderAssetstoreImportView from './views/ImportView';

router.route('girder_assetstore/:id/import', 'girderAssetstoreImport', function (id) {
    // Fetch the assetstore by id, then render the view.
    const assetstore = new AssetstoreModel({ _id: id });
    assetstore.once('g:fetched', function () {
        events.trigger('g:navigateTo', GirderAssetstoreImportView, {
            model: assetstore
        });
    }).once('g:error', function () {
        router.navigate('assetstores', { trigger: true });
    }).fetch();
});
