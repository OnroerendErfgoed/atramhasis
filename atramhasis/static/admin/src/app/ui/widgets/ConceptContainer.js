define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/json',
  'dojo/window',
  'dojo/dom-style',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/ConceptContainer.html',
  './ConceptDetail'
], function (
  declare,
  array,
  lang,
  domConstruct,
  domClass,
  JSON,
  wind,
  domStyle,
  _WidgetBase,
  _TemplatedMixin,
  template,
  ConceptDetail
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'concept-container',
    languageController: null,
    listController: null,
    conceptSchemeController: null,
    _tabs: null,
    _tabIndex: 0,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('ConceptContainer::postCreate');
      this._tabs = [];
      this._calculateBodyHeight();
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('ConceptContainer::startup');
    },

    _calculateBodyHeight: function() {
       var win = wind.getBox();
      var footerheight = 30;
      var headerheight = 60;
      var padding = 80;
      domStyle.set(this.panelNode, 'max-height', win.h - footerheight - headerheight - padding + 'px');
      return (win.h - footerheight - headerheight - padding);
    },

    openTab: function (content, scheme) {
      console.debug('ConceptContainer::openTab', content);
      var tab = this._getTabByContentId(content.id);
      if (tab) {
        this._activateTab(tab.id);
      }
      else {
        this._createTab(content, scheme);
      }
    },

    _createTab: function (content, scheme) {
      console.debug('ConceptContainer::_createTab', content);
      var newId = this._tabIndex++;

      //create tab panel
      var panel = domConstruct.create("div", {
        'class': "tab-panel"
      }, this.panelNode);

      var panelContent = domConstruct.create('div', {
        'class': 'tab-panel-content'
      }, panel);

      // create tab content
      var conceptDetail = new ConceptDetail({
        concept: content,
        scheme: scheme,
        maxHeight: this._calculateBodyHeight(),
        languageController: this.languageController,
        listController: this.listController,
        conceptSchemeController: this.conceptSchemeController
      }, panelContent);
      conceptDetail.startup();

      //create tab button
      var tab = domConstruct.create("li", {
        'class': "tab"
      }, this.tabNode);
      domConstruct.create("a", {
        'innerHTML': content.label,
        'href': "#/tabs/tab/" + newId,
        'onclick': lang.hitch(this, function (evt) {
          evt.preventDefault();
          this._activateTab(newId);
        })
      }, tab);
      domConstruct.create("a", {
        'innerHTML': 'x',
        'href': "#/tabs/tab/" + newId + "/close",
        'onclick': lang.hitch(this, function (evt) {
          evt.preventDefault();
          this._destroyTab(newId);
        })
      }, tab);

      this._tabs.push({
        id: newId,
        tab: tab,
        panel: panel,
        content: conceptDetail
      });

      this._activateTab(newId);
    },

    _getTab: function (tabId) {
      console.debug('ConceptContainer::_getTab', tabId);
      var tabs = array.filter(this._tabs, function (tab) {
        return tab.id == tabId;
      });
      return tabs.length > 0 ? tabs[0] : null;
    },

    _getTabByContentId: function (contentId) {
      console.debug('ConceptContainer::_getTabByContentId', contentId);
      var tabs = array.filter(this._tabs, function (tab) {
        return tab.content && tab.content.id == contentId;
      });
      return tabs.length > 0 ? tabs[0] : null;
    },

    _activateTab: function (tabId) {
      console.debug('ConceptContainer::_activateTab', tabId);
      //show panel & set tab active
      array.forEach(this._tabs, function (tab) {
        if (tab.id == tabId) {
          domClass.add(tab.panel, 'active');
          domClass.add(tab.tab, 'active');
        }
        else {
          domClass.remove(tab.panel, 'active');
          domClass.remove(tab.tab, 'active');
        }
        if (tab.content && tab.content.activate) tab.content.activate();
      });
    },

    _destroyTab: function (tabId) {
      console.debug('ConceptContainer::_destroyTab', tabId);
      var tab = this._getTab(tabId);

      if (tab.content && tab.content.destroy) tab.content.destroy();

      domConstruct.destroy(tab.tab);
      domConstruct.destroy(tab.panel);
      this._tabs = array.filter(this._tabs, function (tab) { return tab.id != tabId});

      //activate last tab
      if (this._tabs.length > 0) {
        this._activateTab(this._tabs[this._tabs.length - 1].id);
      }
    }
  });
});
