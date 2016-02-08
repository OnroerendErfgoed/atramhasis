define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/json',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/ConceptDetail.html'
], function (
  declare,
  array,
  lang,
  domConstruct,
  domClass,
  JSON,
  _WidgetBase,
  _TemplatedMixin,
  template
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'concept-detail',
    concept: null,
    scheme: null,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('ConceptDetail::postCreate');
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('ConceptDetail::startup');

      this._setData();
    },

    _setData: function() {

      // set view data
      this.conceptTitleViewNode.innerHTML = '<strong>' + this.scheme + ' : ' + this.concept.label + '</strong>';
      this.idViewNode.innerHTML = 'ID: ' + this.concept.id;
      this.typeViewNode.innerHTML = 'TYPE: ' + this.concept.type;
      this.uriViewNode.innerHTML = 'URI: ';
      domConstruct.create('a', { href: this.concept.uri, innerHTML: this.concept.uri, target: '_blank' }, this.uriViewNode);

    }
  });
});