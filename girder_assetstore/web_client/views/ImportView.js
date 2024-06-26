import $ from 'jquery';

import BrowserWidget from '@girder/core/views/widgets/BrowserWidget';
import router from '@girder/core/router';
import View from '@girder/core/views/View';
import { restRequest } from '@girder/core/rest';

import { assetstoreImportViewMap } from '@girder/core/views/body/AssetstoresView';
import { AssetstoreType } from '@girder/core/constants';

import AssetstoreImportPage from '../templates/girderAssetstoreImport.pug';

const GirderAssetstoreImportView = View.extend({
    events: {
        'submit .g-gas-import-form': function (e) {
            e.preventDefault();
            this.$('.g-validation-failed-message').empty();

            const importPath = this.$('#g-gas-import-path').val().trim();
            const destinationType = this.$('#g-gas-import-dest-type').val();
            const destinationId = this.$('#g-gas-import-dest-id').val().trim().split(/\s/)[0];

            if (!destinationId) {
                this.$('.g-validation-failed-message').html('Invalid Destination ID');
                return;
            }

            this.$('.g-submit-gas-import').addClass('disabled');
            this.assetstore.off().on('g:imported', function () {
                router.navigate(destinationType + '/' + destinationId, { trigger: true });
            }, this).on('g:error', function (err) {
                this.$('.g-submit-gas-import').removeClass('disabled');
                this.$('.g-validation-failed-message').html(err.responseJSON.message);
            }, this).import({
                importPath,
                destinationId,
                destinationType,
                progress: true
            });
        },
        'click .g-open-browser': '_openBrowser'
    },

    initialize: function (settings) {
        if (settings && settings.assetstore) {
            this.assetstore = settings.assetstore;
        }

        this._browserWidgetView = new BrowserWidget({
            parentView: this,
            titleText: 'Destination',
            helpText: 'Browse to a location to select it as the destination.',
            submitText: 'Select Destination',
            validate: function (model) {
                const isValid = $.Deferred();
                if (!model) {
                    isValid.reject('Please select a valid root.');
                } else {
                    isValid.resolve();
                }
                return isValid.promise();
            }
        });

        this.listenTo(this._browserWidgetView, 'g:saved', function (val) {
            this.$('#g-gas-import-dest-id').val(val.id);
            const model = this._browserWidgetView._hierarchyView.parentModel;
            const modelType = model.get('_modelType');
            this.$('#g-gas-import-dest-type').val(modelType);

            // Make a rest request to get the resource path
            restRequest({
                url: `resource/${val.id}/path`,
                method: 'GET',
                data: { type: modelType }
            }).done((result) => {
                // Only add the resource path if the value wasn't altered
                if (this.$('#g-gas-import-dest-id').val() === val.id) {
                    this.$('#g-gas-import-dest-id').val(`${val.id} (${result})`);
                }
            });
        });

        this.render();
    },

    render: function () {
        if (!this.assetstore) {
            return this;
        }
        const metadata = this.assetstore.get('girder_assetstore_meta') || {};

        this.$el.html(AssetstoreImportPage({
            assetstore: this.assetstore,
            metadata
        }));

        return this;
    },

    _openBrowser: function () {
        this._browserWidgetView.setElement($('#g-dialog-container')).render();
    }
});

assetstoreImportViewMap[AssetstoreType.GIRDER] = GirderAssetstoreImportView;

export default GirderAssetstoreImportView;
