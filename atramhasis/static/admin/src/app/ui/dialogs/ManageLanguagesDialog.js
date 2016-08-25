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
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  'dojo/text!./templates/ManageLanguagesDialog.html',
  'dijit/ConfirmDialog',
  '../../utils/DomUtils',
  './LanguageDialog',
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
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  template,
  ConfirmDialog,
  DomUtils,
  LanguageDialog
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'manage-languages-dialog',
    title: 'Manage languages',
    languageController: null,
    _langStore: null,
    _langGrid: null,

    postCreate: function () {
      this.inherited(arguments);

      this._langStore = this.languageController.getLanguageStore();
      this._langGrid = this._createGrid({
        collection: this._langStore
      }, this.langGridNode);

      this._editLanguageDialog = new LanguageDialog({
        edit: true
      });
      this._editLanguageDialog.startup();

      on(this._editLanguageDialog, 'edit.language', lang.hitch(this, function(evt) {
        this._editLanguage(evt.language);
      }));
    },

    startup: function () {
      this.inherited(arguments);
      this._langGrid.startup();
      this._langGrid.resize();
    },

    _createGrid: function(options, node) {
      var columns = {
        id: {
          label: "ID",
          field: "id"
        },
        name: {
          label: "Name",
          field: "name"
        },
        actions: {
          label: '',
          renderCell: lang.hitch(this, function (object) {
            if (object.id === undefined) {
              return null;
            }
            var div = domConstruct.create('div', {'class': 'dGridHyperlink'});
            domConstruct.create('a', {
              href: '#',
              title: 'Edit language',
              className: 'fa fa-pencil',
              innerHTML: '',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                this._showEditLanguageDialog(object);
              })
            }, div);

            domConstruct.create('a', {
              href: '#',
              title: 'Remove language',
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
        noDataMessage: 'No languages found',
        loadingMessage: 'Fetching data..'
      }, node);

      grid.on('dgrid-error', function(event) {
        console.log(event.error.message);
      });

      return grid;
    },

    hide: function () {
      this.inherited(arguments);
    },

    show: function () {
      this.inherited(arguments);
      this._reset();
    },

    _addLangClick: function (evt) {
      console.debug('LanguagesDialog::_okClick');
      evt.preventDefault();
      if (this._validate()) {
        var obj = {
          id: this.codeInputNode.value,
          name: this.nameInputNode.value
        };
        when(this._langStore.add(obj)).then(
          lang.hitch(this, function (lang) {
            var message = 'New language added: ' + lang.name;
            topic.publish('dGrowl', message, {
              'title': 'Languages',
              'sticky': false,
              'channel': 'info'
            });
            this.languageController.updateLanguageStore();
            this._langGrid.refresh();
            this._reset();
          }),
          function (error) {
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
            topic.publish('dGrowl', message, {
              'title': errorJson.message,
              'sticky': true,
              'channel': 'error'
            });
          }
        );
      } else {
        topic.publish('dGrowl', '-Please fill in a language code to add a new language.', {
          'title': 'Invalid values',
          'sticky': true,
          'channel': 'error'
        });
      }
    },

    _cancelClick: function (evt) {
      console.debug('LanguagesDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    _reset: function () {
      this._langGrid.resize();
      this.codeInputNode.value = '';
      this.nameInputNode.value = '';
    },

    _validate: function () {
      if (this.codeInputNode.value.trim() !== '' && this.codeInputNode.value.trim() !== '') {
        return true;
      }
      return false;
    },

    _removeRow: function(language) {
      var content = '<p style="font-size: 15px;">Are you sure you want to remove <strong>'+ language.name +
        '</strong> (ID: ' + language.id + ')?</p>';

      var confirmationDialog = new ConfirmDialog({
        title: 'Delete language',
        content: content,
        baseClass: 'confirm-dialog'
      });
      query('.dijitButton', confirmationDialog.domNode).addClass('button tiny');
      confirmationDialog.closeText.innerHTML = '<i class="fa fa-times"></i>';

      on(confirmationDialog, 'close', function() {
        confirmationDialog.destroy();
      });
      on(confirmationDialog, 'execute', lang.hitch(this, function () {
        this._langStore.remove(language.id).then(function(removedLang) {
          topic.publish('dGrowl', 'Language removed: ' + removedLang.name + ' (' + removedLang.id + ')', {
            'title': 'Languages',
            'sticky': false,
            'channel': 'info'
          });
          this.languageController.updateLanguageStore();
          this._langGrid.refresh();
          this._reset();
        }, function(err) {
          if (err.response && err.response.status === '409' || err.response.status === 409) {
            topic.publish('dGrowl', language.name + ' (' + language.id +
              ') is in use and can\'t be removed', {
              'title': 'Languages',
              'sticky': false,
              'channel': 'warn'
            });
          }
        });

      }));

      confirmationDialog.show();
    },

    _showEditLanguageDialog: function(language) {
      if (this._editLanguageDialog) {
        this._editLanguageDialog.show(language);
      }
    },

    _editLanguage: function(language) {
      when(this._langStore.add(language)).then(
        lang.hitch(this, function (lang) {
          var message = 'Language edited: ' + lang.name;
          topic.publish('dGrowl', message, {
            'title': 'Languages',
            'sticky': false,
            'channel': 'info'
          });
          this.languageController.updateLanguageStore();
          this._langGrid.refresh();
          this._reset();
        }),
        function (error) {
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
          topic.publish('dGrowl', message, {
            'title': errorJson.message,
            'sticky': true,
            'channel': 'error'
          });
        }
      );
    }

  });
});
