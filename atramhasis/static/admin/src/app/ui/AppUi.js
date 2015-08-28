/**
 * Main application user interface.
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/fx',
  'dojo/dom-style',
  'dojo/topic',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./AppUi.html',
  '../utils/DomUtils',
  './widgets/SearchResultsPane'
], function (declare, lang, fx, domStyle, topic, _WidgetBase, _TemplatedMixin, template, domUtils, SearchResultsPane) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    loadingContainer: null,
    staticAppPath: null,
    conceptSchemeController: null,
    conceptController: null,
    _searchResultsPane: null,

    /**
     * Standard widget function.
     * @public
     */
    postCreate: function () {
      this.inherited(arguments);
      console.debug('AppUi::postCreate');
      this._registerLoadingEvents();
      this._fillConceptSchemeSelect(this.conceptSchemeController.conceptSchemeList);

      this._searchResultsPane = new SearchResultsPane({}, this.searchPaneNode);
    },

    /**
     * Standard widget function.
     * @public
     */
    startup: function () {
      this.inherited(arguments);
      console.debug('AppUi::startup');

      this._searchResultsPane.startup();

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

    _fillConceptSchemeSelect: function (options) {
      domUtils.addOptionsToSelect(this.conceptSchemeSelect, {
        data: options,
        idProperty: 'id',
        labelProperty: 'name'
      });
    },

    _search: function (evt) {
      evt.preventDefault();
      var searchParams = {
        conceptScheme: domUtils.getSelectedOption(this.conceptSchemeSelect),
        conceptType: domUtils.getSelectedOption(this.conceptTypeSelect),
        label: this.labelInput.value
      };
      console.debug('AppUi::_search searchParams', searchParams);

      var store = this.conceptController.getConceptStore(searchParams.conceptScheme);
      console.debug('AppUi::_search store', store);
      this._searchResultsPane.setStore(store);

      this._resetSearchInputs();
    },

    _resetSearchInputs: function () {
      console.debug('AppUi::_resetSearchInputs');
      this.labelSearchForm.reset();
    },

    _createConcept: function(evt) {
      evt.preventDefault();
      console.debug('AppUi::_createConcept');
    },

    _importConcept  : function(evt) {
      evt.preventDefault();
      console.debug('AppUi::_importConcept');
    }
  });
});
