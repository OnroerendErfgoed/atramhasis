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
  'dojo/text!./templates/RelationManager.html',
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
    baseClass: 'relation-manager',
    languageController: null,
    listController: null,
    concept: null,
    languageList: null,
    _broaderStore: null,
    _broaderGrid: null,
    _narrowerStore: null,
    _narrowerGrid: null,
    _relatedStore: null,
    _relatedGrid: null,
    _memberOfStore: null,
    _memberOfGrid: null,
    _subordinateStore: null,
    _subordinateGrid: null,
    _index: 0,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('RelationManager::postCreate');

      var TrackableMemory = declare([Memory, Trackable]);

      //array.forEach(this.concept.notes, lang.hitch(this, function(item){
      //  item.id = this._index++;
      //  this._noteStore.put(item);
      //}));
      this._broaderStore = new TrackableMemory({ data: this.concept.broader });
      this._broaderGrid = this._createGrid({
        collection: this._broaderStore
      }, this.broaderGridNode);

      this._narrowerStore = new TrackableMemory({ data: this.concept.narrower });
      this._narrowerGrid = this._createGrid({
        collection: this._narrowerStore
      }, this.narrowerGridNode);

      this._relatedStore = new TrackableMemory({ data: this.concept.related });
      this._relatedGrid = this._createGrid({
        collection: this._relatedStore
      }, this.relatedGridNode);

      this._memberOfStore = new TrackableMemory({ data: this.concept.member_of });
      this._memberOfGrid = this._createGrid({
        collection: this._memberOfStore
      }, this.memberOfGridNode);

      this._subordinateStore = new TrackableMemory({ data: this.concept.subordinate_arrays });
      this._subordinateGrid = this._createGrid({
        collection: this._subordinateStore
      }, this.subordinateGridNode);
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('RelationManager::startup');
      this._broaderGrid.startup();
      this._narrowerGrid.startup();
      this._relatedGrid.startup();
      this._memberOfGrid.startup();
      this._subordinateGrid.startup();
    },

    _createGrid: function(options, node) {
      var columns = {
        label: {
          label: '',
        },
        remove: {
          label: '',
          renderCell: lang.hitch(this, function (object) {
            if (object.id === undefined) {
              return null;
            }
            var div = domConstruct.create('div', {'class': 'dGridHyperlink'});
            domConstruct.create('a', {
              href: '#',
              title: 'Remove note',
              className: 'fa fa-trash',
              innerHTML: '',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                //this._removeRow(object.id);
              })
            }, div);
            return div;
          })
        }
      };

      var grid = new (declare([OnDemandGrid, DijitRegistry, ColumnResizer]))({
        className: "dgrid-autoheight",
        collection: options.collection,
        columns: columns,
        showHeader: false,
        noDataMessage: '',
        loadingMessage: 'Fetching data..'
      }, node);

      grid.on('dgrid-error', function(event) {
        console.log(event.error.message);
      });

      return grid;
    },

    getData: function() {
      return [];
    },

    _addBroader: function(evt) {
      evt ? evt.preventDefault() : null;

    },

    _addNarrower: function(evt) {
      evt ? evt.preventDefault() : null;
    },

    _addRelated: function(evt) {
      evt ? evt.preventDefault() : null;

    },

    _addMemberOf: function(evt) {
      evt ? evt.preventDefault() : null;

    },

    _addSubordinateArray: function(evt) {
      evt ? evt.preventDefault(): null;
    },

    _removeRow: function(rowId) {
      this._noteStore.remove(rowId);
    },

    _addRow: function(row) {
      console.log('ADD ROW', row);
      this._noteStore.add(row);
    },

    _validate: function(note) {
      var valid = true;

      if (!note.language || note.language === '') {
        valid = false;
      }
      if (!note.type || note.type === '') {
        valid = false;
      }
      if (!note.note || note.note === '') {
        valid = false;
      }

      return valid;
    }

  });
});