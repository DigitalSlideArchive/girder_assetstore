import EditAssetstoreWidget from '@girder/core/views/widgets/EditAssetstoreWidget';
import { AssetstoreType } from '@girder/core/constants';
import { wrap } from '@girder/core/utilities/PluginUtils';

import GirderAssetstoreEditFieldsTemplate from '../templates/girderAssetstoreEditFields.pug';

/**
 * Adds Girder assetstore-specific fields to the edit dialog.
 */
wrap(EditAssetstoreWidget, 'render', function (render) {
    render.call(this);

    if (this.model.get('type') === AssetstoreType.GIRDER) {
        this.$('.g-assetstore-form-fields').append(
            GirderAssetstoreEditFieldsTemplate({
                assetstore: this.model
            })
        );
    }
    return this;
});

EditAssetstoreWidget.prototype.fieldsMap[AssetstoreType.GIRDER] = {
    get: function () {
        return {
            url: this.$('#g-edit-gas-url').val(),
            prefix: this.$('#g-edit-gas-path-prefix').val(),
            apiKey: this.$('#g-edit-gas-api-key').val(),
            username: this.$('#g-edit-gas-username').val(),
            password: this.$('#g-edit-gas-password').val()
        };
    },
    set: function () {
        const metadata = this.model.get('girder_assetstore_meta');
        this.$('#g-edit-gas-url').val(metadata.url);
        this.$('#g-edit-gas-path-prefix').val(metadata.prefix);
        this.$('#g-edit-gas-api-key').val(metadata.apiKey);
        this.$('#g-edit-gas-username').val(metadata.username);
        this.$('#g-edit-gas-password').val(metadata.password);
    }
};
