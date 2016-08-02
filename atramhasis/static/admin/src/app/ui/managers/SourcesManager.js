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
  'dojo/text!./templates/SourcesManager.html',
  'dstore/Memory',
  'dstore/Trackable',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  '../../utils/DomUtils',
  '../dialogs/SourcesDialog'
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
  SourcesDialog
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'sources-manager',
    languageController: null,
    listController: null,
    concept: null,
    languageList: null,
    _sourcesStore: null,
    _sourcesGrid: null,
    _sourcesDialog: null,
    _index: 0,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('SourcesManager::postCreate');

      this.trackableMemory = declare([Memory, Trackable]);
      this._sourcesStore = new this.trackableMemory({ data: [] });
      if (this.concept) {
        array.forEach(this.concept.sources, lang.hitch(this, function (item) {
          item.id = this._index++;
          this._sourcesStore.put(item);
        }));
      }
      this._createGrid({
        collection: this._sourcesStore
      }, this.sourcesGridNode);

      this._sourcesDialog = new SourcesDialog({
        parentNode: this
      });
      on(this._sourcesDialog, 'add.source', lang.hitch(this, function(evt) {
        this._doAddSource(evt);
      }));
      on(this._sourcesDialog, 'edit.source', lang.hitch(this, function(evt) {
        this._doEditSource(evt);
      }));
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('SourcesManager::startup');
      this._sourcesDialog.startup();
      this._sourcesGrid.startup();
      this._sourcesGrid.resize();
    },

    reset: function() {
      if (this._sourcesDialog) { this._sourcesDialog.reset(); }
      var TrackableMemory = declare([Memory, Trackable]);
      this._sourcesStore = new TrackableMemory({ data: [] });
      this._sourcesGrid.set('collection', this._sourcesStore);
    },

    _createGrid: function(options, node) {
      var columns = {
        citation: {
          label: "Citation",
          field: "citation",
          renderCell: function(object) {
            if (object) {
              var div = domConstruct.create('div', {innerHTML: object.citation});
              return div;
            }
          }
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
              title: 'Edit source',
              className: 'fa fa-pencil',
              innerHTML: '',
              style: 'margin-right: 12px;',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                this._editSource(object);
              })
            }, div);
            domConstruct.create('a', {
              href: '#',
              title: 'Remove source',
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
        noDataMessage: 'No sources found',
        loadingMessage: 'Fetching data..'
      }, node);

      this._sourcesGrid = grid;

      grid.on('dgrid-error', function(event) {
        console.log(event.error.message);
      });
    },

    getData: function() {
      var sources = {
        sources: this._sourcesStore.data
      };
      return sources;
    },

    setConcept: function(concept) {
      if (concept) {
        this.concept = concept;
        this._sourcesStore = new this.trackableMemory({ data: [] });
        array.forEach(this.concept.sources, lang.hitch(this, function (item) {
          item.id = this._index++;
          this._sourcesStore.put(item);
        }));
        this._sourcesGrid.set('collection', this._sourcesStore);
      }
    },

    _addSource: function(evt) {
      evt ? evt.preventDefault(): null;
      this._sourcesDialog.show();
    },

    _editSource: function(source) {
      this._sourcesDialog.show(source);
    },

    _doAddSource: function(source) {
      var newSource = {
        citation: source.citation
      };
      console.log(newSource);
      this._sourcesStore.add(newSource);
    },

    _doEditSource: function(source) {
      var editSource = {
        citation: source.citation,
        id: source.id
      };
      console.log(editSource);
      this._sourcesStore.put(editSource);
    },

    _removeRow: function(rowId) {
      this._sourcesStore.remove(rowId);
    }
  });
});