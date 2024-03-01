import _ from 'underscore';

import AssetstoresView from '@girder/core/views/body/AssetstoresView';
import { AssetstoreType } from '@girder/core/constants';
import { wrap } from '@girder/core/utilities/PluginUtils';

import GirderAssetstoreImportButtonTemplate from '../templates/girderAssetstoreImportButton.pug';
import GirderAssetstoreCardTemplate from '../templates/girderAssetstoreCard.pug';

wrap(AssetstoresView, 'render', function (render) {
    render.call(this);

    const selector = '.g-assetstore-info-section[assetstore-type="' + AssetstoreType.GIRDER + '"]';

    _.each(this.$(selector), function (el) {
        const $el = this.$(el);
        const assetstore = this.collection.get($el.attr('cid'));
        const metadata = assetstore.get('girder_assetstore_meta') || {};

        $el.append(GirderAssetstoreCardTemplate({ metadata }));

        $el.parent().find('.g-assetstore-buttons').append(
            GirderAssetstoreImportButtonTemplate({ assetstore })
        );
    }, this);

    this.$('.g-gas-import-button').tooltip({
        delay: 100
    });
    return this;
});
