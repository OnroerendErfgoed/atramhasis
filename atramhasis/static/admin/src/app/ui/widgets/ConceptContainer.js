define([
  'dojo/_base/declare',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/ConceptContainer.html',
  'dijit/layout/TabContainer',
  'dijit/layout/ContentPane'
], function (declare, _WidgetBase, _TemplatedMixin,template, TabContainer, ContentPane) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'concept-container',

    postCreate: function () {
      this.inherited(arguments);
      console.debug('ConceptContainer::postCreate');
      //this._tabContainer = new TabContainer({
      //  //style: "width: 100%; height: 100%"
      //}, this.tabContainerNode);
      //var cp1 = new ContentPane({
      //     title: "cp1",
      //     content: "cp1"
      //});
      //this._tabContainer.addChild(cp1);
      //  var cp2 = new ContentPane({
      //     title: "cp2",
      //     content: "cp2"
      //});
      //this._tabContainer.addChild(cp2);


      //http://www.elated.com/articles/javascript-tabs/
      //http://codepen.io/wallaceerick/full/ojtal/
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('ConceptContainer::startup');
      //this._tabContainer.startup();
    }
  });
});
