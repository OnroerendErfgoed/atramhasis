/**
 * Main application user interface.
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/fx',
  'dojo/_base/array',
  'dojo/dom-style',
  'dojo/topic',
  'dojo/on',
  'dojo/window',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/AppUi.html',
  'dijit/layout/ContentPane',
  'dijit/layout/TabContainer',
  'dijit/layout/LayoutContainer',
  '../utils/DomUtils',
  './widgets/SearchPane',
  './widgets/ConceptDetail',
  './widgets/SlideMenu',
  '../utils/ErrorUtils'
], function (
  declare,
  lang,
  fx,
  array,
  domStyle,
  topic,
  on,
  wind,
  _WidgetBase,
  _TemplatedMixin,
  template,
  ContentPane,
  TabContainer,
  LayoutContainer,
  domUtils,
  SearchPane,
  ConceptDetail,
  SlideMenu,
  errorUtils
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

      on(window, 'resize', lang.hitch(this, function() { this._calculateHeight() }));
    },

    /**
     * Standard widget function.
     * @public
     */
    startup: function () {
      this.inherited(arguments);
      console.debug('AppUi::startup');

      var ui = this._buildInterface();
      ui.startup();
      this._searchPane.startup();
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

    _buildInterface: function () {
      console.debug('AppUi::createView');

      this._calculateHeight();
      //main layout container
      var appContainer = new LayoutContainer({
        design: 'headline',
        id: 'appContainer'
      }, this.conceptContainerNode);

      //body of main layout
      this._container = new TabContainer({
        tabPosition: 'bottom'
      });

      appContainer.addChild(new ContentPane({
        content: this._container,
        region: 'center',
        baseClass: 'appBody'
      }));
      this._createHelpTab(this._container);

      appContainer.startup();
      return appContainer;
    },

    _createHelpTab: function (tabContainer) {
      console.debug('AppUi::_createHelpTab');
      tabContainer.addChild(new ContentPane({
        tabId: 'help',
        title: 'Info',
        content: '<h1>help</h1>',
        closable: false
      }));
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

    _openConcept: function(conceptId, scheme) {
      if (this._getTab(conceptId)) {
        this._openTab(this._getTab(conceptId));
        return;
      }
      this.conceptController.getConcept(scheme, conceptId).then(
        lang.hitch(this, function (data) {
          var conceptDetail = new ConceptDetail({
            concept: data,
            conceptId: conceptId,
            conceptLabel: data.label,
            scheme: scheme,
            //maxHeight: this._calculateBodyHeight(),
            languageController: this.languageController,
            listController: this.listController,
            conceptSchemeController: this.conceptSchemeController
          });
          on(conceptDetail, 'concept.save', lang.hitch(this, function(evt) {
            this._saveConcept(conceptDetail, evt.concept, evt.schemeId);
          }));
          conceptDetail.startup();
          this._addTab(conceptDetail);
        }));
    },

    _createSearchPane: function (node) {
      this._searchPane = new SearchPane({
        conceptSchemeList: this.conceptSchemeController.conceptSchemeList,
        appUi: this
      }, node);
      this.own(
        on(this._searchPane, 'row-select', lang.hitch(this, function (evt) {
          console.debug('catch select event', evt);
          this._openConcept(evt.data.id, evt.scheme);
        }))
      );
    },

    /* Tab container functions*/
    /**
     * Opent een tab in de tabcontainer.
     * @param {Object} child Tab die wordt geopend
     */
    _openTab: function(child) {
      this._container.selectChild(child);
    },

    /**
     * Sluit een tab in de tabcontainer en verwijdert de content uit de DOM.
     * @param {Object} child Tab die wordt gesloten
     */
    _closeTab: function(child) {
      console.debug('AppUi::_closeTab ', child.tabId);
      this._container.removeChild(child);
      child.destroyRecursive();
    },

    /**
     * Zoekt een tab en geeft die terug
     * @param {string} tabId ID van de tab
     * @returns {Contentpane} de gevonden tab of null
     * @private
     */
    _getTab: function(tabId) {
      var tabs = array.filter(this._container.getChildren(), function (tab) {
        return tab.tabId === tabId;
      });

      if(tabs.length > 0) {
        return tabs[0];
      }
      else {
        return null;
      }
    },

    /**
     * Voegt een nieuwe tab toe in de tabcontainer.
     * @param {Object} content Content die wordt toegevoegd in de tab.
     */
    _addTab: function(content) {
      var tab = content;
      tab.tabId = content.conceptId;
      tab.title = content.conceptLabel;
      tab.closable = true;
      tab.onClose = lang.hitch(this, function() {
        this._closeTab(tab);
      });
      this._container.addChild(tab);
      this._container.selectChild(tab);
    },
    /*end tabcontainer*/

    _calculateHeight: function () {
      var win = wind.getBox();
      var footerheight = 30;
      var headerheight = 60;
      domStyle.set(this.appContentContainer, 'height', win.h - footerheight - headerheight + 'px');
      if (this._container) {
        this._container.resize();
      }
    },

    _saveConcept: function(view, concept, schemeId) {
      console.debug('ConceptContainer::_saveConcept', concept);

      this.conceptController.saveConcept(concept, schemeId).then(lang.hitch(this, function(res) {
        // save successful
        view._closeEditDialog();
        this._closeTab(view);
        this._openConcept(res.id, schemeId);
        topic.publish('dGrowl', 'The concept was successfully saved.', {
          'title': 'Save successful',
          'sticky': false,
          'channel': 'info'
        });
      }), function(err) {
        var parsedError = errorUtils.parseError(err);
        topic.publish('dGrowl', parsedError.message, {
          'title': parsedError.title,
          'sticky': true,
          'channel': 'error'
        });
      });
    }
  });
});
