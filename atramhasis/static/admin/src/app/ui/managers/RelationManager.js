define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/dom-style',
  'dojo/json',
  'dojo/topic',
  'dojo/on',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/RelationManager.html',
  'dstore/Memory',
  'dstore/Trackable',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  '../../utils/DomUtils',
  '../dialogs/AddRelationDialog'
], function (
  declare,
  array,
  lang,
  domConstruct,
  domClass,
  domStyle,
  JSON,
  topic,
  on,
  _WidgetBase,
  _TemplatedMixin,
  template,
  Memory,
  Trackable,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  DomUtils,
  AddRelationDialog
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'relation-manager',
    languageController: null,
    listController: null,
    conceptSchemeController: null,
    concept: null,
    scheme: null,
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
    _relationStore: null,
    _addRelationDialog: null,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('RelationManager::postCreate');
      var TrackableMemory = declare([Memory, Trackable]);

      this._broaderStore = new TrackableMemory({ data: this.concept ? this.concept.broader : [] });
      this._broaderGrid = this._createGrid({
        collection: this._broaderStore
      }, this.broaderGridNode);

      this._narrowerStore = new TrackableMemory({ data: this.concept ? this.concept.narrower : [] });
      this._narrowerGrid = this._createGrid({
        collection: this._narrowerStore
      }, this.narrowerGridNode);

      this._relatedStore = new TrackableMemory({ data: this.concept ? this.concept.related : [] });
      this._relatedGrid = this._createGrid({
        collection: this._relatedStore
      }, this.relatedGridNode);

      this._memberOfStore = new TrackableMemory({ data: this.concept ? this.concept.member_of : [] });
      this._memberOfGrid = this._createGrid({
        collection: this._memberOfStore
      }, this.memberOfGridNode);

      this._subordinateStore = new TrackableMemory({ data: this.concept ? this.concept.subordinate_arrays : [] });
      this._subordinateGrid = this._createGrid({
        collection: this._subordinateStore
      }, this.subordinateGridNode);

      this._relationStore = this.conceptSchemeController.getConceptSchemeTree(this.scheme);
      this._addRelationDialog = new AddRelationDialog({
        parentNode: this,
        relationStore: this._relationStore,
        scheme: this.scheme
      });
      this._addRelationDialog.startup();
      this.own(
        on(this._addRelationDialog, 'ok', lang.hitch(this, function (evt) {
          this._addRelation(evt.conceptId, evt.conceptLabel, evt.conceptPath, evt.relation);
        }))
      );

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

    setScheme: function (scheme) {
      this.scheme = scheme;
      this._relationStore = this.conceptSchemeController.getConceptSchemeTree(this.scheme);
      this._addRelationDialog.setScheme(scheme);
    },

    reset: function() {
      var TrackableMemory = declare([Memory, Trackable]);
      this._broaderStore = new TrackableMemory({ data: [] });
      this._broaderGrid.set('collection', this._broaderStore);
      this._narrowerStore = new TrackableMemory({ data: [] });
      this._narrowerGrid.set('collection', this._narrowerStore);
      this._relatedStore = new TrackableMemory({ data: [] });
      this._relatedGrid.set('colleciton', this._relatedStore);
      this._memberOfStore = new TrackableMemory({ data: [] });
      this._memberOfGrid.set('collection', this._memberOfStore);
      this._subordinateStore = new TrackableMemory({ data: [] });
      this._subordinateGrid.set('collection', this._subordinateStore);
    },

    _createGrid: function(options, node) {
      var columns = {
        label: {
          label: ''
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
                this._removeRow(object.id, options.collection);
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
      var relations = {};
      relations.related = array.map(this._relatedStore.data, function(item) {
        var con = {};
        con.id = item.id;
        return con;
      }, this);
      relations.narrower = array.map(this._narrowerStore.data, function(item) {
        var con = {};
        con.id = item.id;
        return con;
      }, this);
      relations.broader = array.map(this._broaderStore.data, function(item) {
        var con = {};
        con.id = item.id;
        return con;
      }, this);
      /* jshint -W106 */
      relations.member_of = array.map(this._memberOfStore.data, function(item) {
        var con = {};
        con.id = item.id;
        return con;
      }, this);
      relations.subordinate_arrays = array.map(this._subordinateStore.data, function(item) {
        var con = {};
        con.id = item.id;
        return con;
      }, this);
      /* jshint +W106 */

      return relations;
    },

    _addRelation: function(id, label, path, relation) {
      var store = relation;

      var found = array.some(store.data, function (item) {
        return item.id == id;
      });
      if (!found) {
        store.add({id: id, label: label, path: path});
        return true;
      }
      return false;
    },

    _addBroader: function(evt) {
      evt ? evt.preventDefault() : null;
      this._addRelationDialog.show(this._broaderStore, this._relationStore);
    },

    _addNarrower: function(evt) {
      evt ? evt.preventDefault() : null;
      this._addRelationDialog.show(this._narrowerStore, this._relationStore);
    },

    _addRelated: function(evt) {
      evt ? evt.preventDefault() : null;
      this._addRelationDialog.show(this._relatedStore, this._relationStore);
    },

    _addMemberOf: function(evt) {
      evt ? evt.preventDefault() : null;
      this._addRelationDialog.show(this._memberOfStore, this._relationStore);
    },

    _addSubordinateArray: function(evt) {
      evt ? evt.preventDefault(): null;
      this._addRelationDialog.show(this._subordinateStore, this._relationStore);
    },

    _removeRow: function(rowId, store) {
      store.remove(rowId);
    }
  });
});
