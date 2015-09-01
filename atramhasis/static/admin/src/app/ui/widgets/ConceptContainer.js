define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/ConceptContainer.html'
], function (declare, array, lang, domConstruct, domClass, _WidgetBase, _TemplatedMixin, template) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'concept-container',
    _tabs: null,
    _tabIndex: 0,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('ConceptContainer::postCreate');
      this._tabs = [];
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('ConceptContainer::startup');
    },

    openTab: function (content) {
      console.debug('ConceptContainer::openTab TODO', content);
      //open or create new tab
      //check on content
    },

    _createTab: function (content) {
      console.debug('ConceptContainer::_createTab', content);
      var newId = this._tabIndex++;

      //create tab panel
      var panel = domConstruct.create("div", {
        'innerHTML': "<p>tab " + newId + "</p>",
        'class': "tab-panel"
      }, this.panelNode);

      //create tab button
      var tab = domConstruct.create("li", {
        'class': "tab"
      }, this.tabNode);
      domConstruct.create("a", {
        'innerHTML': 'tab' + newId,
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
        content: content
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
