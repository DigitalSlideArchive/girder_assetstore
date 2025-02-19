/* global girder */
import _ from 'underscore';

import GirderAssetstoreImportButtonTemplate from '../templates/girderAssetstoreImportButton.pug';
import GirderAssetstoreCardTemplate from '../templates/girderAssetstoreCard.pug';

const AssetstoresView = girder.views.body.AssetstoresView;
const { AssetstoreType } = girder.constants;
const { wrap } = girder.utilities.PluginUtils;

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
