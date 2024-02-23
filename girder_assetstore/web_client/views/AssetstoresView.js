import _ from 'underscore';

import AssetstoresView from '@girder/core/views/body/AssetstoresView';
import { AssetstoreType } from '@girder/core/constants';
import { wrap } from '@girder/core/utilities/PluginUtils';

import GirderAssetstoreButtonTemplate from '../templates/girderAssetstoreImportButton.pug';

wrap(AssetstoresView, 'render', function (render) {
    render.call(this);

    const selector = '.g-assetstore-info-section[assetstore-type="' + AssetstoreType.GIRDER + '"]';

    _.each(this.$(selector), function (el) {
        const $el = this.$(el);
        const assetstore = this.collection.get($el.attr('cid'));

        $el.parent().find('.g-assetstore-buttons').append(
            GirderAssetstoreButtonTemplate({assetstore})
        );
    }, this);

    this.$('.g-gas-import-button').tooltip({
        delay: 100
    });
    return this;
});
