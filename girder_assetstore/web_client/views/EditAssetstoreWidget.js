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
                assetstore: this.model,
            })
        );
    }
    return this;
});

EditAssetstoreWidget.prototype.fieldsMap[AssetstoreType.GIRDER] = {
    get: function () {
        return {
            url: this.$('#g-new-gas-url').val(),
            username: this.$('#g-new-gas-username').val(),
            password: this.$('#g-new-gas-password').val(),
            prefix: this.$('#g-new-gas-path-prefix').val(),
        };
    },
    set: function () {
        const girderInfo = this.model.get('girder_meta');
        this.$('#g-edit-gas-url').val(girderInfo.url);
        this.$('#g-edit-gas-username').val(girderInfo.username);
        this.$('#g-edit-gas-password').val(girderInfo.password);
        this.$('#g-edit-gas-path-prefix').val(girderInfo.prefix);
    }
};
