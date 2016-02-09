define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-class',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/SearchPane.html',
  'dgrid/OnDemandGrid',
  'dgrid/Keyboard',
  'dgrid/Selection',
  'dojo/dom-construct',
  'dojo/topic',
  '../../utils/DomUtils'
], function (
  declare,
  array,
  lang,
  domClass,
  _WidgetBase,
  _TemplatedMixin,
  template,
  OnDemandGrid,
  Keyboard,
  Selection,
  domConstruct,
  topic,
  domUtils
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    conceptSchemeList: null,
    appUi: null,
    _grid: null,
    _scheme: null,


    postCreate: function () {
      this.inherited(arguments);
      console.debug('SearchPane::postCreate');
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('SearchPane::startup');
      this._fillConceptSchemeSelect(this.conceptSchemeList);
      this._createGrid(this.gridNode);
      this._grid.startup();
    },

    init: function (scheme, store) {
      console.debug('SearchPane::init',scheme, store);
      this._scheme = scheme;
      this._grid.set('collection', store);
      console.log(this._grid.get('collection'));
    },

    _createGrid: function (node) {
      console.debug('SearchPane::_createGrid');

      var grid = this._grid = new declare([ OnDemandGrid, Keyboard, Selection ])({
        columns: {
          id: 'ID',
          concept: {
            label: 'Concept',
            renderCell: function(object) {
              var div = domConstruct.create('div', {
                'class': "slideMenuGridCell",
                innerHTML: '<h3>' + object.label + '</h3><p>TYPE: ' + object.type + '</p><p>URI: ' + object.uri + '</p>'
              });
              return div;
            }
          }
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
        console.debug('SearchPane row selected: ', event.rows);
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
        console.debug('SearchPane row de-selected: ', event.rows);
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

    _fillConceptSchemeSelect: function (options) {
      domUtils.addOptionsToSelect(this.conceptSchemeSelect, {
        data: options,
        idProperty: 'id',
        labelProperty: 'name'
      });
    },

    _search: function (evt) {
      evt.preventDefault();
      var schemeId = domUtils.getSelectedOption(this.conceptSchemeSelect);
      if (schemeId == -1) {
        topic.publish('dGrowl', "You have to select a scheme.", {'title': "", 'sticky': false, 'channel':'warn'});
        return;
      }
      var filter = {
        type: domUtils.getSelectedOption(this.conceptTypeSelect),
        label: this.labelInput.value,
        sort: '+label'
      };
      console.debug('SearchPane::_search searchParams', schemeId, filter);
      var store = this.appUi.conceptController.getConceptStore(schemeId).filter(filter);
      this.init(schemeId, store);
      this.appUi._slideMenu._slideOpen();
      this._resetSearchInputs();
    },

    _resetSearchInputs: function () {
      console.debug('SearchPane::_resetSearchInputs');
      this.labelSearchForm.reset();
    },

    _createConcept: function(evt) {
      evt.preventDefault();
      console.debug('SearchPane::_createConcept');
      this.appUi._createConcept(evt);
    },

    _importConcept  : function(evt) {
      evt.preventDefault();
      console.debug('SearchPane::_importConcept');
      this.appUi._importConcept(evt);
    },

    _editLanguages: function (evt) {
      evt.preventDefault();
      console.debug('SearchPane::_editLanguages');
      this.appUi._editLanguages(evt);
    },

    _editConceptScheme: function (evt) {
      evt.preventDefault();
      console.debug('SearchPane::_editConceptScheme');
      this.appUi._editConceptScheme(evt);
    }
  });
});
