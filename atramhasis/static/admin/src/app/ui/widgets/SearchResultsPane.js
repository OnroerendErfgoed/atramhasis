define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-class',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/SearchResultsPane.html',
  'dgrid/OnDemandGrid',
  'dgrid/Keyboard',
  'dgrid/Selection'
], function (declare, array, lang, domClass, _WidgetBase, _TemplatedMixin, template, OnDemandGrid, Keyboard, Selection) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    _grid: null,
    _scheme: null,


    postCreate: function () {
      this.inherited(arguments);
      console.debug('SearchResultsPane::postCreate');
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('SearchResultsPane::startup');
      this._createGrid(this.gridNode);
      this._grid.startup();
    },

    init: function (scheme, store) {
      console.debug('SearchResultsPane::init',scheme, store);
      this._scheme = scheme;
      this._grid.set('collection', store);
      console.log(this._grid.get('collection'));
    },

    _createGrid: function (node) {
      console.debug('SearchResultsPane::_createGrid');

      var grid = this._grid = new declare([ OnDemandGrid, Keyboard, Selection ])({
        columns: {
          id: 'ID',
          label: 'Label',
          type: 'Type',
          uri: 'URI'
        },
        sort: {
          property: 'label'
        },
        selectionMode: 'extended',
        cellNavigation: false,
        loadingMessage: 'Loading data...',
        noDataMessage: 'No results found.',
        collection: null
      }, node);

      grid.on('dgrid-select', lang.hitch(this, function (event) {
        console.debug('SearchResultsPane row selected: ', event.rows);
        array.forEach(event.rows, function (row) {
          this._rowSelect(row);
        }, this);

        // Iterate through all currently-selected items
        //for (var id in grid.selection) {
        //    if (grid.selection[id]) {
                // ...
            //}
        //}
      }));
      grid.on('dgrid-deselect', lang.hitch(this, function (event) {
        console.debug('SearchResultsPane row de-selected: ', event.rows);
        array.forEach(event.rows, function (row) {
          this._rowDeSelect(row);
        }, this);
      }));
    },

    _rowSelect: function (row) {
      this.emit('row-select', {data: row.data, scheme: this._scheme});
    },

    _rowDeSelect: function (row) {
      this.emit('row-deselect', {data: row.data, scheme: this._scheme});
    },

    _toggleHeight: function (evt) {
      evt.preventDefault();
      console.debug('SearchResultsPane::_expand');
      if (!domClass.contains(this.domNode, "search-results-expanded")) {
        domClass.add(this.domNode, "search-results-expanded");
        domClass.remove(this.domNode, "search-results-closed");
      }
      else {
        domClass.remove(this.domNode, "search-results-expanded");
        domClass.add(this.domNode, "search-results-closed");
      }
    }
  });
});
