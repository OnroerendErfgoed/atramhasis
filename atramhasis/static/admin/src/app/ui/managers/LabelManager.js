define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/dom-style',
  'dojo/json',
  'dojo/topic',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/LabelManager.html',
  'dstore/Memory',
  'dstore/Trackable',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  '../../utils/DomUtils'
], function (
  declare,
  array,
  lang,
  domConstruct,
  domClass,
  domStyle,
  JSON,
  topic,
  _WidgetBase,
  _TemplatedMixin,
  template,
  Memory,
  Trackable,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  DomUtils
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'label-manager',
    languageController: null,
    listController: null,
    concept: null,
    languageList: null,
    _labelStore: null,
    _labelGrid: null,
    _index: 0,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('LabelManager::postCreate');
      DomUtils.addOptionsToSelect(this.labelTypeSelectNode, {
        data: this.listController.getLabelTypes(),
        idProperty: 'value',
        labelProperty: 'label'
      });
      DomUtils.addOptionsToSelect(this.languageSelectNode, {
        data: this.languageList,
        idProperty: 'id',
        labelProperty: 'name'
      });
      var TrackableMemory = declare([Memory, Trackable]);
      this._labelStore = new TrackableMemory({ data: [] });
      array.forEach(this.concept.labels, lang.hitch(this, function(item){
        item.id = this._index++;
        this._labelStore.put(item);
      }));
      this._createGrid({
        collection: this._labelStore
      }, this.labelGridNode);
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('LabelManager::startup');
      this._labelGrid.startup();
      this._labelGrid.resize();
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
          formatter: lang.hitch(this, function (value, object) {
            var lang = array.filter(this.languageList, function (obj) {
              return obj.id === value;
            })[0];
            return lang.name;
          })
        },
        type: {
          label: "Type",
          field: "type",
          formatter: lang.hitch(this, function (value, object) {
            var lang = array.filter(this.listController.getLabelTypes(), function (obj) {
              return obj.value === value;
            })[0];
            return lang.label;
          })
        },
        remove: {
          label: 'Remove',
          renderCell: lang.hitch(this, function (object) {
            if (object.id === undefined) {
              return null;
            }
            var div = domConstruct.create('div', {'class': 'dGridHyperlink'});
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
      return this._labelStore.data;
    },

    _addLabel: function(evt) {
      evt ? evt.preventDefault() : null;

      var label = {
        id: this._index++,
        language: DomUtils.getSelectedOption(this.languageSelectNode),
        type: DomUtils.getSelectedOption(this.labelTypeSelectNode),
        label: this.labelTitleNode.value
      };

      if (this._validate(label)) {
        this._addRow(label);
      } else {
        topic.publish('dGrowl', 'Please fill in the fields for a new label', {'title': "Error", 'sticky': true, 'channel':'error'});
      }
    },

    _removeRow: function(rowId) {
      this._labelStore.remove(rowId);
    },

    _addRow: function(row) {
      console.log('ADD ROW', row);
      this._labelStore.add(row);
    },

    _validate: function(label) {
      var valid = true;

      if (!label.language || label.language === '') {
        valid = false;
      }
      if (!label.type || label.type === '') {
        valid = false;
      }
      if (!label.label || label.label === '') {
        valid = false;
      }

      return valid;
    }

  });
});