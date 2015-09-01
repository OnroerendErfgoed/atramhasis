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
  './widgets/SearchResultsPane',
  './widgets/ConceptContainer'
], function (declare, lang, fx, domStyle, topic, on, _WidgetBase, _TemplatedMixin, template, domUtils, SearchResultsPane,
             ConceptContainer) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    loadingContainer: null,
    staticAppPath: null,
    conceptSchemeController: null,
    conceptController: null,
    _searchResultsPane: null,
    _conceptContainer: null,

    /**
     * Standard widget function.
     * @public
     */
    postCreate: function () {
      this.inherited(arguments);
      console.debug('AppUi::postCreate');
      this._registerLoadingEvents();
      this._fillConceptSchemeSelect(this.conceptSchemeController.conceptSchemeList);

      this._createSearchResultsPane(this.searchPaneNode);
      this._conceptContainer = new ConceptContainer({}, this.conceptContainerNode);
    },

    /**
     * Standard widget function.
     * @public
     */
    startup: function () {
      this.inherited(arguments);
      console.debug('AppUi::startup');

      this._searchResultsPane.startup();
      this._conceptContainer.startup();

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
      var schemeId = domUtils.getSelectedOption(this.conceptSchemeSelect);
      if (schemeId == -1) {
        topic.publish('dGrowl', "You have to select a scheme.", {'title': "", 'sticky': false, 'channel':'warn'});
        return;
      }
      var filter = {
        type: domUtils.getSelectedOption(this.conceptTypeSelect),
        label: this.labelInput.value
      };
      console.debug('AppUi::_search searchParams', schemeId, filter);
      var store = this.conceptController.getConceptStore(schemeId).filter(filter);
      this._searchResultsPane.init(schemeId, store);

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
    },

    _editLanguages: function (evt) {
      evt.preventDefault();
      console.debug('AppUi::_editLanguages');
    },

    _editConceptScheme: function (evt) {
      evt.preventDefault();
      console.debug('AppUi::_editConceptScheme');
    },

    _createSearchResultsPane: function (node) {
      this._searchResultsPane = new SearchResultsPane({}, node);
      this.own(
        on(this._searchResultsPane, 'row-select', lang.hitch(this, function (evt) {
          console.debug('catch select event', evt);
          this.conceptController.getConcept(evt.scheme, evt.data.id).then(
            lang.hitch(this, function (response) {
              this._conceptContainer.openTab(response);
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
