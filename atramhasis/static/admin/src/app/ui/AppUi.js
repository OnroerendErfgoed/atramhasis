/**
 * Main application user interface.
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/fx',
  'dojo/dom-style',
  'dojo/topic',
  'dojo/on',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./AppUi.html',
  '../utils/DomUtils',
  './widgets/SearchPane',
  './widgets/ConceptContainer',
  './widgets/SlideMenu'
], function (
  declare,
  lang,
  fx,
  domStyle,
  topic,
  on,
  _WidgetBase,
  _TemplatedMixin,
  template,
  domUtils,
  SearchPane,
  ConceptContainer,
  SlideMenu
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    loadingContainer: null,
    staticAppPath: null,
    conceptSchemeController: null,
    conceptController: null,
    languageController: null,
    listController: null,
    _searchPane: null,
    _conceptContainer: null,
    _slideMenu: null,

    /**
     * Standard widget function.
     * @public
     */
    postCreate: function () {
      this.inherited(arguments);
      console.debug('AppUi::postCreate');
      this._registerLoadingEvents();
      //this._fillConceptSchemeSelect(this.conceptSchemeController.conceptSchemeList);

      this._createSlideMenu(this.menuContainerNode);
      this._conceptContainer = new ConceptContainer({
        languageController: this.languageController,
        listController: this.listController,
        conceptSchemeController: this.conceptSchemeController,
        conceptController: this.conceptController
      }, this.conceptContainerNode);
    },

    /**
     * Standard widget function.
     * @public
     */
    startup: function () {
      this.inherited(arguments);
      console.debug('AppUi::startup');

      this._searchPane.startup();
      this._conceptContainer.startup();

      this._slideMenu._slideOpen();

      this._hideLoading();
    },

    /**
     * Hide the 'Loading'-overlay.
     * @public
     */
    _hideLoading: function () {
      var node = this.loadingContainer;
      fx.fadeOut({
        node: node,
        onEnd: function (node) {
          domStyle.set(node, 'display', 'none');
        },
        duration: 1000
      }).play();
    },

    /**
     * Show the 'Loading'-overlay.
     * @public
     */
    _showLoading: function (message) {
      if (!message) message = "";
      var node = this.loadingContainer;
      query(".loadingMessage", node).innerHTML(message);

      domStyle.set(node, 'display', 'block');
      fx.fadeIn({
        node: node,
        duration: 1
      }).play();
    },

    /**
     * Listen to events to show/hide the loading overlay
     * @private
     */
    _registerLoadingEvents: function () {
      this.own(
        topic.subscribe('standby.show',lang.hitch(this, function(evt){
          this._showLoading(evt.message);
        })),
        topic.subscribe('standby.stop',lang.hitch(this, function(){
          this._hideLoading();
        }))
      );
    },

    _createConcept: function(evt) {
      evt.preventDefault();
      console.debug('AppUi::_createConcept');
    },

    _importConcept  : function(evt) {
      evt.preventDefault();
      console.debug('AppUi::_importConcept');
    },

    _editLanguages: function (evt) {
      evt.preventDefault();
      console.debug('AppUi::_editLanguages');
    },

    _editConceptScheme: function (evt) {
      evt.preventDefault();
      console.debug('AppUi::_editConceptScheme');
    },

    _createSlideMenu: function(node) {
      this._slideMenu = new SlideMenu({
        overlayContainer: this.menuOverlayContainer
        }, node);
      this._slideMenu.startup();
      this._createSearchPane(this._slideMenu.menuNode);
    },

    _closeMenu: function(evt) {
      evt ? evt.preventDefault() : null;
      this._slideMenu._slideClose();
    },

    _toggleMenu: function(evt) {
      evt ? evt.preventDefault() : null;
      this._slideMenu._toggleMenu();
    },

    _createSearchPane: function (node) {
      this._searchPane = new SearchPane({
        conceptSchemeList: this.conceptSchemeController.conceptSchemeList,
        appUi: this
      }, node);
      this.own(
        on(this._searchPane, 'row-select', lang.hitch(this, function (evt) {
          console.debug('catch select event', evt);
          this.conceptController.getConcept(evt.scheme, evt.data.id).then(
            lang.hitch(this, function (response) {
              this._conceptContainer.openTab(response, evt.scheme);
            }),
            function (error) {
              topic.publish('dGrowl', error, {'title': "Error", 'sticky': true, 'channel':'error'});
            }
          );
        }))
      );
    }
  });
});
