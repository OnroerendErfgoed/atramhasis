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
  'dojo/text!./templates/MatchesManager.html',
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
  on,
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
    conceptSchemeController: null,
    concept: null,
    scheme: null,
    matchTypes: null,
    languageList: null,
    _broadStore: null,
    _broadGrid: null,
    _narrowStore: null,
    _narrowGrid: null,
    _relatedStore: null,
    _relatedGrid: null,
    _exactStore: null,
    _exactGrid: null,
    _closeStore: null,
    _closeGrid: null,
    _index: 0,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('RelationManager::postCreate');
      var TrackableMemory = declare([Memory, Trackable]);

      this._broadStore = new TrackableMemory({ data: [] });
      this._broadGrid = this._createGrid({
        collection: this._broadStore
      }, this.broadGridNode);

      this._narrowStore = new TrackableMemory({ data: [] });
      this._narrowGrid = this._createGrid({
        collection: this._narrowStore
      }, this.narrowGridNode);

      this._relatedStore = new TrackableMemory({ data: [] });
      this._relatedGrid = this._createGrid({
        collection: this._relatedStore
      }, this.relatedGridNode);

      this._exactStore = new TrackableMemory({ data: [] });
      this._exactGrid = this._createGrid({
        collection: this._exactStore
      }, this.exactGridNode);

      this._closeStore = new TrackableMemory({ data: [] });
      this._closeGrid = this._createGrid({
        collection: this._closeStore
      }, this.closeGridNode);

      this._loadMatches(this.concept.matches);
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('RelationManager::startup');
      this._broadGrid.startup();
      this._narrowGrid.startup();
      this._relatedGrid.startup();
      this._exactGrid.startup();
      this._closeGrid.startup();
    },

    _createGrid: function(options, node) {
      var columns = {
        label: {
          label: '',
          get: function(object) {
            return object.data.label;
          }
        },
        uri: {
          label: '',
          renderCell: function(object){
            if (object && object.data) {
              return domConstruct.create('a', { href: object.data.uri, target: '_blank',
                innerHTML: '<i class="fa fa-external-link"></i>&nbsp;&nbsp;' + object.data.uri });
            }
          }
        },
        remove: {
          label: '',
          renderCell: lang.hitch(this, function (object) {
            console.log(object);
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

    _loadMatches: function(matches) {
      if (matches) {
        if (matches.broad) {
          array.forEach(matches.broad, function (match) {
            this.conceptSchemeController.getMatch(match, 'broad').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._broadStore);
            }));
          }, this);
        }
        if (matches.close) {
          array.forEach(matches.close, function (match) {
            this.conceptSchemeController.getMatch(match, 'close').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._closeStore);
            }));
          }, this);
        }
        if (matches.exact) {
          array.forEach(matches.exact, function (match) {
            this.conceptSchemeController.getMatch(match, 'exact').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._exactStore);
            }));
          }, this);
        }
        if (matches.narrow) {
          array.forEach(matches.narrow, function (match) {
            this.conceptSchemeController.getMatch(match, 'narrow').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._narrowStore);
            }));
          }, this);
        }
        if (matches.related) {
          array.forEach(matches.related, function (match) {
            this.conceptSchemeController.getMatch(match, 'related').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._relatedStore);
            }));
          }, this);
        }
      }
    },

    getData: function() {
      return [];
    },

    _addMatch: function(match, store) {
      var found = array.some(store.data, function (item) {
        return item.data.id == match.data.id;
      });
      if (!found) {
        store.add(match);
        return true;
      }
      return false;
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

    _addMatches: function(evt) {
      evt ? evt.preventDefault() : null;
    },

    _removeRow: function(rowId, store) {
      store.remove(rowId);
    }
  });
});