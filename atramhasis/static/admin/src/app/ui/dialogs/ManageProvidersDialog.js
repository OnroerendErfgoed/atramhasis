define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/topic',
  'dojo/_base/lang',
  'dojo/query',
  'dojo/on',
  'dojo/when',
  'dojo/_base/array',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  'dojo/text!./templates/ManageProvidersDialog.html',
  'dijit/ConfirmDialog',
  '../../utils/DomUtils',
  'dojo/NodeList-manipulate'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  topic,
  lang,
  query,
  on,
  when,
  array,
  domConstruct,
  domClass,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  template,
  ConfirmDialog,
  domUtils
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'manage-providers-dialog',
    title: 'Manage providers',
    providerController: null,
    languageController: null,
    _providerStore: null,
    _providerGrid: null,

    postCreate: function () {
      this.inherited(arguments);
      this._providerStore = this.providerController.getProviderStore();
      this._providerGrid = this._createGrid({
        collection: this._providerStore
      }, this.providerGridNode);
      this.languageController.getLanguageStore().fetch().then(lang.hitch(this, function(languages) {
        domUtils.addOptionsToSelect(this.defaultLangNode, {
          data: languages,
          idProperty: 'id',
          labelProperty: 'name',
          placeholder: 'Choose a language'
        });
        domUtils.addOptionsToSelect(this.displayLangNode, {
          data: languages,
          idProperty: 'id',
          labelProperty: 'name',
          placeholder: 'Choose a language'
        });
      }));
    },

    startup: function () {
      this.inherited(arguments);
      this._providerGrid.startup();
      this._providerGrid.resize();
    },

    hide: function () {
      this.inherited(arguments);
    },

    show: function () {
      this.inherited(arguments);
      this._reset();
    },

    _cancelClick: function (evt) {
      console.debug('ProvidersDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    _reset: function () {
      domClass.add(this.providerFormNode, 'hide');
    },

    _createGrid: function(options, node) {
      var columns = {
        id: {
          label: 'ID',
          field: 'id'
        },
        name: {
          label: 'Conceptscheme uri',
          field: 'conceptscheme_uri'
        },
        uri_pattern: {
          label: 'Uri pattern',
          field: 'uri_pattern'
        },
        type: {
          label: 'Type',
          field: 'type'
        },
        default_language: {
          label: 'Def. lang.',
          field: 'default_language'
        },
        force_display_language: {
          label: 'Displ. lang.',
          field: 'force_display_language'
        },
        id_generation_strategy: {
          label: 'ID gen. strategy',
          field: 'id_generation_strategy'
        },
        subject: {
          label: 'Subject',
          field: 'subject'
        },
        expand_strategy: {
          label: 'Expand strategy',
          field: 'expand_strategy'
        },
        actions: {
          label: '',
          renderCell: lang.hitch(this, function (object) {
            if (object.type !=='SQLAlchemyProvider') {
              return null;
            }
            var div = domConstruct.create('div', {'class': 'dGridHyperlink'});
            domConstruct.create('a', {
              href: '#',
              title: 'Edit provider',
              className: 'fa fa-pencil',
              innerHTML: '',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                // this._showEditLanguageDialog(object);
              })
            }, div);

            domConstruct.create('a', {
              href: '#',
              title: 'Remove provider',
              className: 'fa fa-trash',
              innerHTML: '',
              style: 'margin-left: 10px;',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                this._removeRow(object);
              })
            }, div);
            return div;
          })
        }
      };

      var grid = new (declare([OnDemandGrid, DijitRegistry, ColumnResizer]))({
        collection: options.collection,
        columns: columns,
        noDataMessage: 'No providers found',
        loadingMessage: 'Fetching data..'
      }, node);

      grid.on('dgrid-error', function(event) {
        console.log(event.error.message);
      });

      return grid;
    },

    showProviderForm: function() {
      domClass.remove(this.providerFormNode, 'hide');
    },

    _removeRow: function(provider) {
      var content = '<p style="font-size: 15px;">Are you sure you want to remove provider <strong>'+ provider.id +
        '</strong> (' + provider.conceptscheme_uri + ')?</p>';

      var confirmationDialog = new ConfirmDialog({
        title: 'Delete provider',
        content: content,
        baseClass: 'confirm-dialog'
      });
      query('.dijitButton', confirmationDialog.domNode).addClass('button tiny');
      confirmationDialog.closeText.innerHTML = '<i class="fa fa-times"></i>';

      on(confirmationDialog, 'close', function() {
        confirmationDialog.destroy();
      });
      on(confirmationDialog, 'execute', lang.hitch(this, function () {
        this._providerStore.remove(provider.id).then(function(removedProvider) {
          topic.publish('dGrowl', 'Provider removed: ' + removedProvider.id, {
            'title': 'Provider',
            'sticky': false,
            'channel': 'info'
          });
          // this.languageController.updateLanguageStore();
          this._providerGrid.refresh();
          this._reset();
        }, function(err) {
          if (err.response && err.response.status === '409' || err.response.status === 409) {
            topic.publish('dGrowl', provider.id + ' (' + provider.conceptscheme_uri +
              ') is in use and can\'t be removed', {
              'title': 'Provider',
              'sticky': false,
              'channel': 'warn'
            });
          }
        });

      }));

      confirmationDialog.show();
    },

    _addProvider: function () {
      console.debug('addprovider');

      var provider = {
        id: this.idNode.value.trim() ? this.idNode.value.trim() : undefined,
        conceptscheme_uri: this.uriNode.value.trim(),
        uri_pattern: this.uriPatternNode.value.trim(),
        id_generation_strategy: domUtils.getSelectedOption(this.idStrategyNode),
        expand_strategy: domUtils.getSelectedOption(this.expandStrategyNode)
      };

      this._providerStore.add(provider).then(
        lang.hitch(this, function (prov) {
          var message = 'New provider added with id ' + prov.id;
          topic.publish('dGrowl', message, {
            'title': 'Languages',
            'sticky': false,
            'channel': 'info'
          });
        }),
        function (error) {
          topic.publish('dGrowl', error.message, {
            'title': 'Error adding provider',
            'sticky': true,
            'channel': 'error'
          });
        });
    }
  });
});
