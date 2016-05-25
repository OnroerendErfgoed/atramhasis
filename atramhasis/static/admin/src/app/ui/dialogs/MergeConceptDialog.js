define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/_base/array',
  'dojo/topic',
  'dojo/dom-construct',
  'dojo/text!./templates/MergeConceptDialog.html'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  array,
  topic,
  domConstruct,
  template
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'merge-concept-dialog',
    title: 'Merge concept or collection',
    scheme: null,
    concept: null,
    _mergeGrid: null,
    _mergeStore: null,

    postCreate: function () {
      this.inherited(arguments);

      this._mergeGrid = this._createGrid({
        collection: this._mergeStore
      }, this.mergeConceptGridNode);
    },

    startup: function () {
      this.inherited(arguments);
      //this._mergeGrid.startup();
    },

    hide: function () {
      this.inherited(arguments);
    },

    _createGrid: function(options, node) {

    },

    _okClick: function (evt) {
      console.debug('MergeConceptDialog::_okClick');
      evt.preventDefault();
      this.emit('concept.merge', {

      });
      this.hide();
    },

    show: function(concept, schemeId) {
      this.inherited(arguments);

    },

    _cancelClick: function (evt) {
      console.debug('MergeConceptDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    }
  });
});
