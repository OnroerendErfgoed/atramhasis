define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/dom-style',
  'dojo/json',
  'dojo/on',
  'dojo/topic',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/LabelManager.html',
  'dstore/Memory',
  'dstore/Trackable',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  '../../utils/DomUtils',
  '../dialogs/LabelsDialog'
], function (
  declare,
  array,
  lang,
  domConstruct,
  domClass,
  domStyle,
  JSON,
  on,
  topic,
  _WidgetBase,
  _TemplatedMixin,
  template,
  Memory,
  Trackable,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  DomUtils,
  LabelsDialog
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'label-manager',
    languageController: null,
    listController: null,
    concept: null,
    languageList: null,
    _labelDialog: null,
    _labelStore: null,
    _labelGrid: null,
    _index: 0,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('LabelManager::postCreate');
      this.trackableMemory = declare([Memory, Trackable]);
      this._labelStore = new this.trackableMemory({ data: [] });
      if (this.concept) {
        array.forEach(this.concept.labels, lang.hitch(this, function (item) {
          item.id = this._index++;
          this._labelStore.put(item);
        }));
      }
      this._createGrid({
        collection: this._labelStore
      }, this.labelGridNode);

      this._labelDialog = new LabelsDialog({
        parentNode: this,
        langList: this.languageList,
        typeList: this.listController.getLabelTypes()
      });
      on(this._labelDialog, 'add.label', lang.hitch(this, function(evt) {
        this._doAddLabel(evt);
      }));
      on(this._labelDialog, 'edit.label', lang.hitch(this, function(evt) {
        this._doEditLabel(evt);
      }));
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('LabelManager::startup');
      this._labelGrid.startup();
      this._labelGrid.resize();
    },

    reset: function() {
      if (this._labelDialog) { this._labelDialog.reset(); }
      var TrackableMemory = declare([Memory, Trackable]);
      this._labelStore = new TrackableMemory({ data: [] });
      this._labelGrid.set('collection', this._labelStore);
    },

    _createGrid: function(options, node) {
      var columns = {
        label: {
          label: "Title",
          field: "label"
        },
        language: {
          label: "Language",
          field: "language",
          formatter: lang.hitch(this, function (value) {
            var lang = array.filter(this.languageList, function (obj) {
              return obj.id === value;
            })[0];
            if (lang) {
              return lang.name;
            } else {
              return '-';
            }
          })
        },
        type: {
          label: "Type",
          field: "type",
          formatter: lang.hitch(this, function (value) {
            var lang = array.filter(this.listController.getLabelTypes(), function (obj) {
              return obj.value === value;
            })[0];
            return lang.label;
          })
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
              title: 'Edit label',
              className: 'fa fa-pencil',
              innerHTML: '',
              style: 'margin-right: 12px;',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                this._editLabel(object);
              })
            }, div);
            domConstruct.create('a', {
              href: '#',
              title: 'Remove label',
              className: 'fa fa-trash',
              innerHTML: '',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                this._removeRow(object.id);
              })
            }, div);
            return div;
          })
        }
      };

      var grid = new (declare([OnDemandGrid, DijitRegistry, ColumnResizer]))({
        collection: options.collection,
        columns: columns,
        showHeader: false,
        noDataMessage: 'No labels found',
        loadingMessage: 'Fetching data..'
      }, node);

      this._labelGrid = grid;

      grid.on('dgrid-error', function(event) {
        console.log(event.error.message);
      });
    },

    getData: function() {
      var labels = {
        labels: this._labelStore.data
      }
      return labels;
    },

    setConcept: function(concept) {
      if (concept) {
        this.concept = concept;
        this._labelStore = new this.trackableMemory({ data: [] });
        array.forEach(this.concept.labels, lang.hitch(this, function (item) {
          item.id = this._index++;
          this._labelStore.put(item);
        }));
        this._labelGrid.set('collection', this._labelStore);
      }
    },

    updateLanguages: function(languages) {
      if (languages) {
        this.languageList = languages;
        this._labelDialog.updateLanguages(languages);
      }
    },

    _addLabel: function(evt) {
      evt ? evt.preventDefault(): null;
      this._labelDialog.show();
    },

    _editLabel: function(label) {
      this._labelDialog.show(label);
    },

    _doAddLabel: function(label) {
      var newLabel = {
        language: label.lang,
        type: label.labelType,
        label: label.label
      };
      this._labelStore.add(newLabel);
    },

    _doEditLabel: function(label) {
      var editLabel = {
        language: label.lang,
        type: label.labelType,
        label: label.label,
        id: label.id
      };
      this._labelStore.put(editLabel);
    },

    _removeRow: function(rowId) {
      this._labelStore.remove(rowId);
    }
  });
});