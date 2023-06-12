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
    _broaderStore: null,
    _broaderGrid: null,
    _narrowerStore: null,
    _narrowerGrid: null,
    _relatedStore: null,
    _relatedGrid: null,
    _memberOfStore: null,
    _memberOfGrid: null,
    _membersStore: null,
    _membersGrid: null,
    _subordinateStore: null,
    _subordinateGrid: null,
    _superordinatesCollStore: null,
    _superordinatesCollGrid: null,
    _index: 0,
    _isCollection: null,
    _relationStore: null,
    _addRelationDialog: null,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('RelationManager::postCreate');
      this.trackableMemory = declare([Memory, Trackable]);

      this._broaderStore = new this.trackableMemory({ data: this.concept ? this.concept.broader : [] });
      this._broaderGrid = this._createGrid({
        collection: this._broaderStore,
        type: 'broader'
      }, this.broaderGridNode);

      this._narrowerStore = new this.trackableMemory({ data: this.concept ? this.concept.narrower : [] });
      this._narrowerGrid = this._createGrid({
        collection: this._narrowerStore,
        type: 'narrower'
      }, this.narrowerGridNode);

      this._relatedStore = new this.trackableMemory({ data: this.concept ? this.concept.related : [] });
      this._relatedGrid = this._createGrid({
        collection: this._relatedStore,
        type: 'related'
      }, this.relatedGridNode);

      this._memberOfStore = new this.trackableMemory({ data: this.concept ? this.concept.member_of : [] });
      this._memberOfGrid = this._createGrid({
        collection: this._memberOfStore,
        type: 'memberOf'
      }, this.memberOfGridNode);

      this._membersStore = new this.trackableMemory({ data: this.concept ? this.concept.members : [] });
      this._membersGrid = this._createGrid({
        collection: this._membersStore,
        type: 'members'
      }, this.membersGridNode);

      this._subordinateStore = new this.trackableMemory({ data: this.concept ? this.concept.subordinate_arrays : [] });
      this._subordinateGrid = this._createGrid({
        collection: this._subordinateStore,
        type: 'subordinate'
      }, this.subordinateGridNode);

      this._superordinatesCollStore = new this.trackableMemory({ data: this.concept ? this.concept.superordinates : [] });
      this._superordinatesCollGrid = this._createGrid({
        collection: this._superordinatesCollStore,
        type: 'superordinate'
      }, this.superordinatesCollGridNode);

      this._relationStore = this.conceptSchemeController.getConceptSchemeTree(this.scheme);
      this._addRelationDialog = new AddRelationDialog({
        parentNode: this,
        relationStore: this._relationStore,
        concept: this.concept,
        scheme: this.scheme
      });
      this._addRelationDialog.startup();
      this.own(
        on(this._addRelationDialog, 'ok', lang.hitch(this, function (evt) {
          this._addRelation(evt.conceptId, evt.conceptLabel, evt.conceptPath, evt.relation);
        }))
      );

      if (this.concept && this.concept.type === 'collection') {
        this.setCollectionTypes();
      } else {
        this.setConceptTypes();
      }
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('RelationManager::startup');
      this._broaderGrid.startup();
      this._narrowerGrid.startup();
      this._relatedGrid.startup();
      this._memberOfGrid.startup();
      this._membersGrid.startup();
      this._subordinateGrid.startup();
      this._superordinatesCollGrid.startup();
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
      this._relatedGrid.set('collection', this._relatedStore);
      this._memberOfStore = new TrackableMemory({ data: [] });
      this._memberOfGrid.set('collection', this._memberOfStore);
      this._membersStore = new TrackableMemory({ data: [] });
      this._membersGrid.set('collection', this._membersStore);
      this._subordinateStore = new TrackableMemory({ data: [] });
      this._subordinateGrid.set('collection', this._subordinateStore);
      this._superordinatesCollStore = new TrackableMemory({ data: [] });
      this._superordinatesCollGrid.set('collection', this._superordinatesCollStore);
      this.inferConceptRelationsYesNode.checked = false;
      this.inferConceptRelationsNoNode.checked = false;
    },

    setCollectionTypes: function() {
      this._isCollection = true;
      this.broaderContainerNode.style.display = 'none';
      this.broaderGridNode.style.display = 'none';
      this.narrowerContainerNode.style.display = 'none';
      this.narrowerGridNode.style.display = 'none';
      this.relatedContainerNode.style.display = 'none';
      this.relatedGridNode.style.display = 'none';
      this.subordinateArraysContainerNode.style.display = 'none';
      this.subordinateGridNode.style.display = 'none';

      this.superordinatesCollContainerNode.style.display = 'block';
      this.superordinatesCollGridNode.style.display = 'block';
      this.membersContainerNode.style.display = 'block';
      this.membersGridNode.style.display = 'block';
      this.inferConceptRelationsContainerNode.style.display = 'block';
    },

    setConceptTypes: function() {
      this._isCollection = false;
      this.broaderContainerNode.style.display = 'block';
      this.broaderGridNode.style.display = 'block';
      this.narrowerContainerNode.style.display = 'block';
      this.narrowerGridNode.style.display = 'block';
      this.relatedContainerNode.style.display = 'block';
      this.relatedGridNode.style.display = 'block';
      this.subordinateArraysContainerNode.style.display = 'block';
      this.subordinateGridNode.style.display = 'block';

      this.membersContainerNode.style.display = 'none';
      this.membersGridNode.style.display = 'none';
      this.superordinatesCollContainerNode.style.display = 'none';
      this.superordinatesCollGridNode.style.display = 'none';
      this.inferConceptRelationsContainerNode.style.display = 'none';
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
              title: 'Remove relation',
              className: 'fa fa-trash',
              innerHTML: '',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                this._removeRow(object.id, options.type);
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
      if (!this._isCollection) {
        relations.related = array.map(this._relatedStore.data, function (item) {
          var con = {};
          con.id = item.id;
          return con;
        }, this);
        relations.narrower = array.map(this._narrowerStore.data, function (item) {
          var con = {};
          con.id = item.id;
          return con;
        }, this);
        relations.broader = array.map(this._broaderStore.data, function (item) {
          var con = {};
          con.id = item.id;
          return con;
        }, this);
        /* jshint -W106 */
        relations.subordinate_arrays = array.map(this._subordinateStore.data, function (item) {
          var con = {};
          con.id = item.id;
          return con;
        }, this);
        /* jshint +W106 */
      } else {
        relations.members = array.map(this._membersStore.data, function (item) {
          var con = {};
          con.id = item.id;
          return con;
        }, this);
        relations.superordinates = array.map(this._superordinatesCollStore.data, function (item) {
          var con = {};
          con.id = item.id;
          return con;
        }, this);
        /* jshint -W106 */
        relations.infer_concept_relations = this.inferConceptRelationsYesNode.checked ?
          true : (this.inferConceptRelationsNoNode.checked ? false : undefined);
        /* jshint +W106 */
      }

      /* jshint -W106 */
      relations.member_of = array.map(this._memberOfStore.data, function(item) {
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

    setConcept: function(concept) {
      if (concept) {
        this.concept = concept;
        this._broaderStore = new this.trackableMemory({data: this.concept ? this.concept.broader : []});
        this._broaderGrid.set('collection', this._broaderStore);
        this._narrowerStore = new this.trackableMemory({data: this.concept ? this.concept.narrower : []});
        this._narrowerGrid.set('collection', this._narrowerStore);
        this._relatedStore = new this.trackableMemory({data: this.concept ? this.concept.related : []});
        this._relatedGrid.set('collection', this._relatedStore);
        this._memberOfStore = new this.trackableMemory({data: this.concept ? this.concept.member_of : []});
        this._memberOfGrid.set('collection', this._memberOfStore);
        this._membersStore = new this.trackableMemory({data: this.concept ? this.concept.members : []});
        this._membersGrid.set('collection', this._membersStore);
        this._subordinateStore = new this.trackableMemory({data: this.concept ? this.concept.subordinate_arrays : []});
        this._subordinateGrid.set('collection', this._subordinateStore);
        this._superordinatesCollStore = new this.trackableMemory({data: this.concept ? this.concept.superordinates : []});
        this._superordinatesCollGrid.set('collection', this._superordinatesCollStore);
        /* jshint -W106 */
        if (concept.infer_concept_relations === true) {
          this.inferConceptRelationsYesNode.checked = true;
        }
        else if (concept.infer_concept_relations === false) {
          this.inferConceptRelationsNoNode.checked = true;
        }
        /* jshint +W106 */
        if (this.concept.type === 'collection') {
          this.setCollectionTypes();
        } else {
          this.setConceptTypes();
        }
      }
    },

    _addBroader: function(evt) {
      evt ? evt.preventDefault(): null;
      this._addRelationDialog.show(this._broaderStore, this._relationStore);
    },

    _addNarrower: function(evt) {
      evt ? evt.preventDefault(): null;
      this._addRelationDialog.show(this._narrowerStore, this._relationStore);
    },

    _addRelated: function(evt) {
      evt ? evt.preventDefault(): null;
      this._addRelationDialog.show(this._relatedStore, this._relationStore);
    },

    _addMemberOf: function(evt) {
      evt ? evt.preventDefault(): null;
      this._addRelationDialog.show(this._memberOfStore, this._relationStore);
    },

    _addMembers: function(evt) {
      evt ? evt.preventDefault(): null;
      this._addRelationDialog.show(this._membersStore, this._relationStore);
    },

    _addSubordinateArray: function(evt) {
      evt ? evt.preventDefault(): null;
      this._addRelationDialog.show(this._subordinateStore, this._relationStore);
    },

    _addSuperordinates: function(evt) {
      evt ? evt.preventDefault(): null;
      this._addRelationDialog.show(this._superordinatesCollStore, this._relationStore);
    },

    _removeRow: function(rowId, type) {
      console.log(rowId, type);
      var store = null;
      switch(type) {
        case 'broader': store = this._broaderStore;
          break;
        case 'narrower': store = this._narrowerStore;
          break;
        case 'related': store = this._relatedStore;
          break;
        case 'memberOf': store = this._memberOfStore;
          break;
        case 'members': store = this._membersStore;
          break;
        case 'subordinate': store = this._subordinateStore;
          break;
        case 'superordinate': store = this._superordinatesCollStore;
          break;
      }
      if (store) {
        store.remove(rowId);
      }
    }
  });
});
