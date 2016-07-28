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
  'dojo/promise/all',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/MatchesManager.html',
  'dstore/Memory',
  'dstore/Trackable',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  '../../utils/DomUtils',
  '../dialogs/AddMatchesDialog'
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
  all,
  _WidgetBase,
  _TemplatedMixin,
  template,
  Memory,
  Trackable,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  DomUtils,
  AddMatchesDialog
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'matches-manager',
    languageController: null,
    listController: null,
    conceptSchemeController: null,
    concept: null,
    scheme: null,
    matchTypes: null,
    _loaded: false,
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
    _matchesDialog: null,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('RelationManager::postCreate');
      var TrackableMemory = declare([Memory, Trackable]);

      // init grids
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

      if (this.concept && this.concept.matches) {
        this._loadMatches(this.concept.matches);
      }

      // load add dialog
      this._matchesDialog = new AddMatchesDialog({
        concept: this.concept,
        externalSchemeStore: this.conceptSchemeController.getExternalSchemeStore(),
        conceptSchemeController: this.conceptSchemeController,
        matchTypesList: this.listController.getMatchTypes()
      });
      this._matchesDialog.startup();

      this.own(
        on(this._matchesDialog, 'match.add', lang.hitch(this, function(evt) {
          this._addNewMatch(evt.match, evt.matchType);
        }))
      );
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

    reset: function() {
      var TrackableMemory = declare([Memory, Trackable]);
      this._broadStore = new TrackableMemory({ data: [] });
      this._broadGrid.set('collection', this._broadStore);
      this._narrowStore = new TrackableMemory({ data: [] });
      this._narrowGrid.set('collection', this._narrowStore);
      this._relatedStore = new TrackableMemory({ data: [] });
      this._relatedGrid.set('collection', this._relatedStore);
      this._exactStore = new TrackableMemory({ data: [] });
      this._exactGrid.set('collection', this._exactStore);
      this._closeStore = new TrackableMemory({ data: [] });
      this._closeGrid.set('collection', this._closeStore);

      if (this._matchesDialog) { this._matchesDialog.reset(); }
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
              return domConstruct.create('a', { href: object.data.uri, target: '_blank', title: object.data.uri,
                innerHTML: '<i class="fa fa-external-link"></i>&nbsp;&nbsp;' + object.data.uri });
            }
          }
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
              title: 'Remove match',
              className: 'fa fa-trash',
              innerHTML: '',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                this._removeRow(object.id, object.type);
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
        console.debug(event.error.message);
      });

      return grid;
    },

    setConcept: function(concept) {
      if (concept) {
        this.concept = concept;
        this.reset();
        if (this.concept.matches) {
          this._loadMatches(this.concept.matches);
        }
      }
    },

    _loadMatches: function(matches) {
      if (matches) {
        var promises = [];
        this.loadingMatchesNode.style.display = 'inline-block';
        if (matches.broad) {
          array.forEach(matches.broad, function (match) {
            promises.push(this.conceptSchemeController.getMatch(match, 'broad').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._broadStore);
            })));
          }, this);
        }
        if (matches.close) {
          array.forEach(matches.close, function (match) {
            promises.push(this.conceptSchemeController.getMatch(match, 'close').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._closeStore);
            })));
          }, this);
        }
        if (matches.exact) {
          array.forEach(matches.exact, function (match) {
            promises.push(this.conceptSchemeController.getMatch(match, 'exact').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._exactStore);
            })));
          }, this);
        }
        if (matches.narrow) {
          array.forEach(matches.narrow, function (match) {
            promises.push(this.conceptSchemeController.getMatch(match, 'narrow').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._narrowStore);
            })));
          }, this);
        }
        if (matches.related) {
          array.forEach(matches.related, function (match) {
            promises.push(this.conceptSchemeController.getMatch(match, 'related').then(lang.hitch(this, function (matched) {
              this._addMatch(matched, this._relatedStore);
            })));
          }, this);
        }

        all(promises).then(lang.hitch(this, function(res) {
          this.loadingMatchesNode.style.display = 'none';
          this._loaded = true;
        }));
      }
    },

    getData: function() {
      var data = {};

      if (this._loaded) {
        var matches = {};
        matches.narrow = array.map(this._narrowStore.data, function (item) {
          return item.data.uri;
        });
        matches.broad = array.map(this._broadStore.data, function (item) {
          return item.data.uri;
        });
        matches.related = array.map(this._relatedStore.data, function (item) {
          return item.data.uri;
        });
        matches.close = array.map(this._closeStore.data, function (item) {
          return item.data.uri;
        });
        matches.exact = array.map(this._exactStore.data, function (item) {
          return item.data.uri;
        });
        data.matches = matches;
      } else { // when not all matches are loaded into store => return existing matches
        if (this.concept && this.concept.matches) {
          data.matches = this.concept.matches;
        } else {
          data.matches = {};
        }
      }

      return data;
    },

    _addNewMatch: function(match, matchtype) {
      var store = null;

      switch(matchtype) {
        case 'broad': store = this._broadStore;
          break;
        case 'narrow': store = this._narrowStore;
          break;
        case 'related': store = this._relatedStore;
          break;
        case 'close': store = this._closeStore;
          break;
        case 'exact': store = this._exactStore;
          break;
      }

      if (match && store) {
        var formatMatch = {
          data: {
            id: match.id,
            label: match.label,
            uri: match.uri
          },
          type: match.type
        };
        this._addMatch(formatMatch, store);
      }
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

    _addMatches: function(evt) {
      evt ? evt.preventDefault(): null;
      // open dialog
      this._matchesDialog.show();
    },

    _removeRow: function(rowId, type) {
      var store = null;
      switch(type) {
        case 'broad': store = this._broadStore;
          break;
        case 'close': store = this._closeStore;
          break;
        case 'exact': store = this._exactStore;
          break;
        case 'narrow': store = this._narrowStore;
          break;
        case 'related': store = this._relatedStore;
          break;
      }
      if (store) {
        store.remove(rowId);
      }
    }
  });
});