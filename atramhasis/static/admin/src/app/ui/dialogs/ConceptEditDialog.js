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
  '../managers/NoteManager',
  '../managers/RelationManager',
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
  NoteManager,
  RelationManager,
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
      this._createNotesTab(this.concept);
      this._createRelationsTab(this.concept);
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

    _saveConcept: function(evt) {
      evt ? evt.preventDefault() : null;

      var labelData = this.labelManager.getData();
      console.log(labelData);

      var noteData = this.noteManager.getData();
      console.log(noteData);
    },

    _cancel: function(evt) {
      evt ? evt.preventDefault() : null;
      this.parent._closeEditDialog();
    },

    _createLabelsTab: function(concept) {
      this.languageController.getLanguageStore().fetch().then(lang.hitch(this, function(languages) {
        this.labelManager = new LabelManager({
          languageController: this.languageController,
          listController: this.listController,
          concept: concept,
          languageList: languages
        }, this.labelsNode);
        this.labelManager.startup();
      }));
    },

    _createNotesTab: function(concept) {
      this.languageController.getLanguageStore().fetch().then(lang.hitch(this, function(languages) {
        this.noteManager = new NoteManager({
          languageController: this.languageController,
          listController: this.listController,
          concept: concept,
          languageList: languages
        }, this.notesNode);
        this.noteManager.startup();
      }));
    },

    _createRelationsTab: function(concept) {
      this.languageController.getLanguageStore().fetch().then(lang.hitch(this, function(languages) {
        this.relationManager = new RelationManager({
          languageController: this.languageController,
          listController: this.listController,
          concept: concept,
          languageList: languages
        }, this.relationsNode);
        this.relationManager.startup();
      }));
    }
  });
});