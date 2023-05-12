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
  'dojo/dom-attr',
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
  domAttr,
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
    _editMode: false,

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
    },

    hide: function () {
      this.inherited(arguments);
    },

    show: function () {
      this.inherited(arguments);
    },

    _closeClick: function (evt) {
      evt.preventDefault();
      this._reset(false);
      this.hide();
    },

    _reset: function (delayRefresh) {
      this._editMode = false;
      this._hideProviderForm();
      domAttr.remove(this.idNode, 'disabled');
      domAttr.remove(this.uriNode, 'disabled');
      this.idNode.value = '';
      this.uriNode.value = '';
      this.uriPatternNode.value = '';
      this.subjectNode.value = '';
      this.subjectNode.value = '';
      domUtils.setSelectedOptions(this.idStrategyNode, ['NUMERIC']);
      domUtils.setSelectedOptions(this.expandStrategyNode, ['recurse']);
      domUtils.setSelectedOptions(this.defaultLangNode, ['']);
      domUtils.setSelectedOptions(this.displayLangNode, ['']);
      this._providerGrid.resize();
      if (delayRefresh) {
        setTimeout(lang.hitch(this, function(){ this._providerGrid.refresh(); }), 1000);
      }
      else {
        this._providerGrid.refresh();
      }
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
                this._openProvider(object);
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
                this._removeProvider(object);
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
        console.error(event.error.message);
      });

      return grid;
    },

    _showProviderForm: function() {
      if (this._editMode) {
        domAttr.set(this.idNode, 'disabled', true);
        domAttr.set(this.uriNode, 'disabled', true);
      }
      domClass.remove(this.providerFormNode, 'hide');
      domClass.add(this.providerGridContainerNode, 'hide');
    },

    _hideProviderForm: function() {
      domClass.add(this.providerFormNode, 'hide');
      domClass.remove(this.providerGridContainerNode, 'hide');
    },

    _openProvider: function(provider) {
      this._editMode = true;
      this._setProvider(provider);
      this._showProviderForm();
    },

    _removeProvider: function(provider) {
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
        this._providerStore.remove(provider.id).then(lang.hitch(this, function() {
          topic.publish('dGrowl', 'Provider removed: ' + provider.id, {
            'title': 'Provider',
            'sticky': false,
            'channel': 'info'
          });
          this._reset(true);
        }), function(err) {
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

    _cancelProvider: function() {
      this._reset();
    },

    _saveProvider: function () {
      var subjects = this.subjectNode.value.split(',')
        .map(function(item) {
          return item.trim();
        })
        .filter(function(item) {
          return item.length > 0;
        });

      var provider = {
        id: this.idNode.value.trim() ? this.idNode.value.trim() : undefined,
        conceptscheme_uri: this.uriNode.value.trim(),
        uri_pattern: this.uriPatternNode.value.trim(),
        subject: subjects,
        id_generation_strategy: domUtils.getSelectedOption(this.idStrategyNode),
        expand_strategy: domUtils.getSelectedOption(this.expandStrategyNode),
        default_language: domUtils.getSelectedOption(this.defaultLangNode),
        force_display_language: domUtils.getSelectedOption(this.displayLangNode)
      };

      if (!this._validate(provider)) {
        topic.publish('dGrowl', 'Please fill in all required fields.', {
          'title': 'Provider not valid',
          'sticky': false,
          'channel': 'warn'
        });
        return;
      }

      this._editMode ? this._editProvider(provider) : this._addProvider(provider);
    },

    _setProvider: function(provider) {
      this.idNode.value = provider.id;
      this.uriNode.value = provider.conceptscheme_uri;
      this.uriPatternNode.value = provider.uri_pattern;
      this.subjectNode.value = provider.subject.join(', ');
      if (provider.id_generation_strategy) {
        domUtils.setSelectedOptions(this.idStrategyNode, [provider.id_generation_strategy]);
      }
      if (provider.expand_strategy) {
        domUtils.setSelectedOptions(this.expandStrategyNode, [provider.expand_strategy]);
      }
      if (provider.default_language) {
        domUtils.setSelectedOptions(this.defaultLangNode, [provider.default_language]);
      }
      if (provider.force_display_language) {
        domUtils.setSelectedOptions(this.displayLangNode, [provider.force_display_language]);
      }
    },

    _validate: function (provider) {
      var valid = true;
      if (provider.conceptscheme_uri === '' || provider.uri_pattern === '') {
        valid = false;
      }
      return valid;
    },

    _parseError: function (error) {
      var errorJson = JSON.parse(error.response.data);
      var message = "",
        prop = null;
      array.forEach(errorJson.errors, function (errorObj) {
        for (prop in errorObj) {
          message += "-<em>";
          message += prop;
          message += "</em>: ";
          message += errorObj[prop];
          message += "<br>";
        }
      });
      return message;
    },

    _addProvider: function(provider) {
      this._providerStore.add(provider).then(
        lang.hitch(this, function (prov) {
          var message = 'New provider added with id ' + prov.id;
          topic.publish('dGrowl', message, {
            'title': 'Provider',
            'sticky': false,
            'channel': 'info'
          });
          this._reset(true);
        }),
        lang.hitch(this, function (error) {
          var message = this._parseError(error);
          topic.publish('dGrowl', message, {
            'title': 'Error adding provider',
            'sticky': true,
            'channel': 'error'
          });
        })
      );
    },

    _editProvider: function(provider) {
      this._providerStore.put(provider).then(
        lang.hitch(this, function (prov) {
          var message = 'Provider with id ' + prov.id + ' was saved.';
          topic.publish('dGrowl', message, {
            'title': 'Provider',
            'sticky': false,
            'channel': 'info'
          });
          this._reset();
        }),
        lang.hitch(this, function (error) {
          var message = this._parseError(error);
          topic.publish('dGrowl', message, {
            'title': 'Error editing provider',
            'sticky': true,
            'channel': 'error'
          });
        })
      );
    }
  });
});
