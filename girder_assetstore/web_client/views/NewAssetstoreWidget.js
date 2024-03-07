import NewAssetstoreWidget from '@girder/core/views/widgets/NewAssetstoreWidget';
import { AssetstoreType } from '@girder/core/constants';
import { wrap } from '@girder/core/utilities/PluginUtils';

import GirderAssetstoreCreateTemplate from '../templates/girderAssetstoreCreate.pug';

// Add UI for creating new Girder assetstore.
wrap(NewAssetstoreWidget, 'render', function (render) {
    render.call(this);

    this.$('#g-assetstore-accordion').append(GirderAssetstoreCreateTemplate());
    return this;
});

NewAssetstoreWidget.prototype.events['submit #g-new-gas-form'] = function (e) {
    const formBody = {
        type: AssetstoreType.GIRDER,
        name: this.$('#g-new-gas-name').val(),
        url: this.$('#g-new-gas-url').val(),
        prefix: this.$('#g-new-gas-path-prefix').val(),
        apiKey: this.$('#g-new-gas-api-key').val(),
        username: this.$('#g-new-gas-username').val(),
        password: this.$('#g-new-gas-password').val()
    };

    this.createAssetstore(e, this.$('#g-new-gas-error'), formBody);
};
