define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dstore/Memory',
  'dojo/topic',
  'dojo/dom-construct',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  'dgrid/Selection',
  '../../utils/DomUtils',
  'dojo/text!./templates/AddMatchesDialog.html'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  lang,
  array,
  Memory,
  topic,
  domConstruct,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  Selection,
  domUtils,
  template
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'matches-dialog',
    title: 'Add a match',
    concept: null,
    conceptSchemeController: null,
    externalSchemeStore: null,
    matchTypesList: null,
    _matchesGrid: null,
    _matchesStore: null,

    postCreate: function () {
      this.inherited(arguments);

      this._matchesGrid = this._createGrid({
        collection: this._matchesStore
      }, this.addMatchesGridNode);

      // load and set external scheme list
      this.externalSchemeStore.fetch().then(lang.hitch(this, function(externals) {
        domUtils.addOptionsToSelect(this.externalSchemeSelect, {
          data: externals,
          idProperty: 'id',
          labelProperty: 'label'
        });
      }));

      // set match types
      domUtils.addOptionsToSelect(this.matchTypeSelectNode, {
        data: this.matchTypesList,
        idProperty: 'value',
        labelProperty: 'label'
      });
    },

    startup: function () {
      this.inherited(arguments);
      this._matchesGrid.startup();
    },

    reset: function() {
      this.externalSchemeSelect.selectedIndex = 0;
      this.matchTypeSelectNode.selectedIndex = 0;
      this._matchesStore = new Memory({ data: [] });
      this._matchesGrid.set('collection', this._matchesStore);
      this.searchLabelInput.value = '';
    },

    hide: function () {
      this.reset();
      this.inherited(arguments);
    },

    _createGrid: function(options, node) {
      var columns = {
        label: {
          label: ''
        },
        id: {
          label: ''
        },
        type: {
          label: ''
        },
        link: {
          label: '',
          renderCell: function(object){
            if (object && object.uri) {
              return domConstruct.create('a', { href: object.uri, target: '_blank', title: object.uri,
                innerHTML: '<i class="fa fa-external-link"></i>' });
            }
          }
        }
      };

      var grid = new (declare([OnDemandGrid, DijitRegistry, ColumnResizer, Selection]))({
        collection: options.collection,
        columns: columns,
        selectionMode: 'single',
        showHeader: false,
        noDataMessage: '',
        loadingMessage: 'Fetching data..'
      }, node);

      grid.on('dgrid-error', function(event) {
        console.log(event.error.message);
      });

      return grid;
    },

    _okClick: function (evt) {
      console.debug('MatchesDialog::_okClick');
      evt.preventDefault();

      var matchType = domUtils.getSelectedOption(this.matchTypeSelectNode);
      var selected = null;
      for (var id in this._matchesGrid.selection) {
        if (this._matchesGrid.selection[id]) {
          selected = this._matchesStore.getSync(id);
        }
      }

      if (selected) {
        this.emit('match.add', {
          matchType: matchType,
          match: selected
        });
        this.hide();
      } else {
        // none selected
        // todo dgrowl
      }
    },

    _cancelClick: function (evt) {
      console.debug('MatchesDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    _searchMatches: function(evt)  {
      evt ? evt.preventDefault() : null;

      var externalScheme = domUtils.getSelectedOption(this.externalSchemeSelect);
      var searchLabel = this.searchLabelInput.value;

      if (externalScheme && searchLabel && searchLabel !== '') {
        this._loadStore(externalScheme, searchLabel)
      }
    },

    _loadStore: function(externalScheme, searchLabel) {
      this.conceptSchemeController.searchForConcepts(externalScheme, searchLabel).then(lang.hitch(this,
        function(concepts) {
          this._matchesStore = new Memory({ data: concepts });
          this._matchesGrid.set('collection', this._matchesStore);
          this._matchesGrid.resize();
        }), function(err) {
        console.log(err);
      });

    },

    _validate: function () {
      //return this.auteurInput.value.trim() !== '';
    }
  });
});
