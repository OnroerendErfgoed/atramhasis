define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dijit/tree/ObjectStoreModel',
  'dstore/legacy/DstoreAdapter',
  'dijit/Tree',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/topic',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  '../../utils/DomUtils',
  'dojo/text!./templates/AddMatchesDialog.html'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  ObjectStoreModel,
  DstoreAdapter,
  Tree,
  lang,
  array,
  topic,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  domUtils,
  template
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'matches-dialog',
    title: 'Add a match',
    scheme: null,
    concept: null,
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

    hide: function () {
      this._reset();
      this.inherited(arguments);
    },

    _createGrid: function(options, node) {
      var columns = {
        label: {
          label: ''
        }
      };

      var grid = new (declare([OnDemandGrid, DijitRegistry, ColumnResizer]))({
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

    _okClick: function (evt) {
      console.debug('MatchesDialog::_okClick');
      evt.preventDefault();
    },

    _cancelClick: function (evt) {
      console.debug('MatchesDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    _searchMatches: function(evt)  {
      evt ? evt.preventDefault() : null;
    },

    _reset: function () {
      //this.auteurInput.value = '';
    },

    _validate: function () {
      //return this.auteurInput.value.trim() !== '';
    }
  });
});
