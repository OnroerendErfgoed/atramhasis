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
    _labelStore: null,
    _labelGrid: null,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('LabelManager::postCreate');
      DomUtils.addOptionsToSelect(this.labelTypeSelectNode, {
        data: this.listController.getLabelTypes(),
        idProperty: 'value',
        labelProperty: 'label'
      });
      this.languageController.getLanguageStore().fetch().then(lang.hitch(this, function(results) {
        DomUtils.addOptionsToSelect(this.languageSelectNode, {
          data: results,
          idProperty: 'id',
          labelProperty: 'name'
        });
      }));
      var TrackableMemory = declare([Memory, Trackable]);
      var labels = this.concept.labels;
      this._labelStore = new TrackableMemory({data: []});
      array.forEach(labels, lang.hitch(this, function(item){
        item.id = Math.random();
        this._labelStore.put(item);
      }));
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('LabelManager::startup');
      this._createGrid({
        collection: this._labelStore
      }, this.labelGridNode);
      this._labelGrid.startup();
    },

    _createGrid: function(options, node) {
      var columns = {
        id: 'id',
        label: {
          label: "Title",
          field: "label"
        },
        language: {
          label: "Language",
          field: "language"
        },
        type: {
          label: "Type",
          field: "type"
        }
      };

      var grid = new (declare([OnDemandGrid, DijitRegistry, ColumnResizer]))({
        collection: options.collection,
        columns: columns,
        showHeader: false,
        sort: [
          { attribute: 'label' }
        ],
        noDataMessage: 'No labels found',
        loadingMessage: 'Fetching data..'
      }, node);

      this._labelGrid = grid;

      grid.on('dgrid-error', function(event) {
        // Display an error message above the grid when an error occurs.
        console.log(event.error.message);
      });
    },

    _saveLabels: function(evt) {
      evt ? evt.preventDefault() : null;
    },

    _addLabel: function(evt) {
      evt ? evt.preventDefault() : null;

      var label = {
        id: Math.random(),
        language: DomUtils.getSelectedOption(this.languageSelectNode),
        type: DomUtils.getSelectedOption(this.labelTypeSelectNode),
        label: this.labelTitleNode.value
      };

      if (this._validate(label)) {
        this._addRow(label);
      } else {
        topic.publish('dGrowl', 'Please fill in all label fields', {'title': "Error", 'sticky': true, 'channel':'error'});
      }
    },

    _addRow: function(row) {
      console.log('ADD ROW', row);
      console.log(this._labelStore);
      console.log(this._labelGrid.get('collection'));
      this._labelStore.put(row);
      this._labelGrid.refresh();
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