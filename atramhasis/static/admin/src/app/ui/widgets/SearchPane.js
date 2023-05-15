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
  'dijit/Menu',
  'dijit/MenuItem',
  'dijit/MenuSeparator',
  'dojo/dom-construct',
  'dojo/dom-attr',
  'dojo/topic',
  'dojo/on',
  'dojo/dom-style',
  'dojo/window',
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
  Menu,
  MenuItem,
  MenuSeparator,
  domConstruct,
  domAttr,
  topic,
  on,
  domStyle,
  wind,
  domUtils
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    conceptSchemeList: null,
    baseClass: 'search-pane',
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
      this._calculateGridHeight();
      on(window, 'resize', lang.hitch(this, function() { this._calculateGridHeight() }));
      if (this.appUi.canCreateProviders) {
        domAttr.set(this.manageProvidersButton, 'disabled', false);
      }
    },

    init: function (scheme, store) {
      console.debug('SearchPane::init',scheme, store);
      this._scheme = scheme;
      this._grid.set('collection', store);
    },

    reload: function () {
      console.debug('SearchPane::reload');
      this._grid.set('collection', this.appUi.conceptController.getConceptStore(this._scheme));
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
        selectionMode: 'single',
        cellNavigation: false,
        loadingMessage: 'Loading data...',
        noDataMessage: 'No results found.',
        collection: null
      }, node);

      var contextMenu = this._createContextMenu();
      var collectionContextMenu = this._createCollectionContextMenu();

      grid.on('.dgrid-content .dgrid-row:click', lang.hitch(this, function (event) {
        console.debug('SearchPane row selected: ', event);
        var row = grid.row(event);
        if (row) {
          this._rowSelect(row);
        }
      }));

      grid.on('.dgrid-row:contextmenu', lang.hitch(this, function(evt){
        evt.preventDefault(); // prevent default browser context menu
        var type = grid.row(evt).data.type;
        if (type && type === 'concept') {
          contextMenu.selectedGridItem = grid.row(evt).data;
          // security can be added here
          contextMenu._scheduleOpen(this, null, {x: evt.pageX, y: evt.pageY});
        } else {
          collectionContextMenu.selectedGridItem = grid.row(evt).data;
          // security can be added here
          collectionContextMenu._scheduleOpen(this, null, {x: evt.pageX, y: evt.pageY});
        }
      }));
    },

    _calculateGridHeight: function () {
      var win = wind.getBox();
      var footerheight = 30;
      var headerheight = 60;
      var menuheight = win.h - footerheight - headerheight;
      var form = 326;
      var buttons = 80;
      domStyle.set(this.searchResultsNode, 'height', menuheight - form - buttons + 'px');
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
        labelProperty: 'label'
      });

      this.own(
        on(this.conceptSchemeSelect, 'change', lang.hitch(this, function() {
          this.emit('scheme.changed', {
            schemeId: this.conceptSchemeSelect.value
          });
          // activate buttons for add and import, edit scheme
          domAttr.set(this.addConceptButton, 'disabled', false);
          domAttr.set(this.importConceptButton, 'disabled', false);
          domAttr.set(this.editSchemeButton, 'disabled', false);
          this._search();
        }))
      );
    },

    _createContextMenu: function () {
      var contextMenu = new Menu({});
      var pane = this;

      contextMenu.addChild(new MenuItem({
        label: 'Add narrower concept',
        onClick: lang.hitch(this, function () {
          pane.emit('concept.addnarrower', {
            conceptId: contextMenu.selectedGridItem.id
          });
        })
      }));
      contextMenu.addChild(new MenuItem({
        label: 'Add subordinate array',
        onClick: lang.hitch(this, function () {
          pane.emit('concept.addsubarray', {
            conceptId: contextMenu.selectedGridItem.id
          });
        })
      }));
      contextMenu.addChild(new MenuItem({
        label: 'Edit',
        onClick: lang.hitch(this, function () {
          pane.emit('concept.edit', {
            conceptId: contextMenu.selectedGridItem.id
          });
        })
      }));
      contextMenu.addChild(new MenuItem({
        label: 'Delete',
        onClick: lang.hitch(this, function () {
          pane.emit('concept.delete', {
            conceptId: contextMenu.selectedGridItem.id
          });
        })
      }));
      contextMenu.addChild(new MenuSeparator());
      contextMenu.addChild(new MenuItem({
        label: 'Add concept or collection',
        onClick: lang.hitch(this, function () {
          pane.emit('concept.create');
        })
      }));

      return contextMenu;
    },

    _createCollectionContextMenu: function () {
      var contextMenu = new Menu({});
      var pane = this;

      contextMenu.addChild(new MenuItem({
        label: 'Add member',
        onClick: lang.hitch(this, function () {
          pane.emit('concept.addmember', {
            conceptId: contextMenu.selectedGridItem.id
          });
        })
      }));
      contextMenu.addChild(new MenuItem({
        label: 'Edit',
        onClick: lang.hitch(this, function () {
          pane.emit('concept.edit', {
            conceptId: contextMenu.selectedGridItem.id
          });
        })
      }));
      contextMenu.addChild(new MenuItem({
        label: 'Delete',
        onClick: lang.hitch(this, function () {
          pane.emit('concept.delete', {
            conceptId: contextMenu.selectedGridItem.id
          });
        })
      }));
      contextMenu.addChild(new MenuSeparator());
      contextMenu.addChild(new MenuItem({
        label: 'Add concept or collection',
        onClick: lang.hitch(this, function () {
          pane.emit('concept.create');
        })
      }));

      return contextMenu;
    },

    _search: function (evt) {
      evt ? evt.preventDefault() : null;
      var schemeId = domUtils.getSelectedOption(this.conceptSchemeSelect);

      this.matchInput.value = this.matchInput.value.trim();
      this.labelInput.value = this.labelInput.value.trim();

      if (schemeId == -1) {
        topic.publish('dGrowl', "You have to select a scheme.", {'title': "", 'sticky': false, 'channel':'warn'});
        return;
      }
      var filter = {
        type: domUtils.getSelectedOption(this.conceptTypeSelect),
        label: this.labelInput.value,
        sort: '+label'
      };
      if (this.matchInput.value !== '') {
        filter.match= this.matchInput.value;
      }
      var store = this.appUi.conceptController.getConceptStore(schemeId).filter(filter);
      this.init(schemeId, store);
      this.appUi._slideMenu._slideOpen();
      //this._resetSearchInputs();
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
    },

    _editProviders: function () {
      console.debug('SearchPane::_editProviders');
      this.appUi._editProviders();
    }
  });
});
