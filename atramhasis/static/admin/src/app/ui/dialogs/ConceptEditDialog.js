define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/topic',
  'dijit/Dialog',
  'dijit/_Widget',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  '../../utils/DomUtils',
  '../managers/LabelManager',
  'dojo/text!./templates/ConceptEditDialog.html',
  'dijit/layout/TabContainer',
  'dijit/layout/ContentPane'
], function (
  declare,
  lang,
  topic,
  Dialog,
  _Widget,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  DomUtils,
  LabelManager,
  template
) {
  return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    baseClass: 'concept-edit-dialog',
    concept: null,
    dialog: null,
    parent: null,
    scheme: null,
    languageController: null,
    listController: null,

    /**
     * Standaard widget functie
     */
    postCreate: function () {
      this.inherited(arguments);
      this.dialog = new Dialog({
        title: 'Edit <strong>' + this.concept.label + '</strong>',
        style: 'width: 1000px; min-height: 500px;',
        onHide: lang.hitch(this, function() {
          this.parent._closeEditDialog();
        })
      });
      this.dialog.closeText.innerHTML = '<i class="fa fa-times"></i>';
      this.dialog.set('content', this);

      this._createLabelsTab(this.concept);
    },

    /**
     * Standaard widget functie
     */
    startup: function () {
      this.inherited(arguments);
      this._setData(this.concept);
      this.showDialog();
      this.tabContainer.layout();
      this.dialog.resize();
    },

    _setData: function(concept) {
      this.schemeNode.value = this.scheme;
    },

    /**
     * Toont het dialog
     */
    showDialog: function () {
      this.dialog.show();
    },

    /**
     * Sluit het dialog
     * @private
     */
    _close: function () {
      this.dialog.hide();
    },

    _createLabelsTab: function(concept) {
      this.labelManager = new LabelManager({
        languageController: this.languageController,
        listController: this.listController,
        concept: concept
      }, this.labelsNode);
      this.labelManager.startup();
    }
  });
});