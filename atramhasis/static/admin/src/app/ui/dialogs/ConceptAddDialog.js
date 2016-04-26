define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/topic',
  'dojo/on',
  'dijit/Dialog',
  'dijit/_Widget',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  '../../utils/DomUtils',
  '../managers/LabelManager',
  '../managers/NoteManager',
  '../managers/RelationManager',
  '../managers/MatchesManager',
  '../../utils/DomUtils',
  'dojo/text!./templates/ConceptAddDialog.html',
  'dijit/layout/TabContainer',
  'dijit/layout/ContentPane'
], function (
  declare,
  lang,
  topic,
  on,
  Dialog,
  _Widget,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  DomUtils,
  LabelManager,
  NoteManager,
  RelationManager,
  MatchesManager,
  domUtils,
  template
) {
  return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    baseClass: 'concept-add-dialog',
    dialog: null,
    parent: null,
    scheme: null,
    languageController: null,
    listController: null,
    conceptSchemeController: null,

    /**
     * Standaard widget functie
     */
    postCreate: function () {
      this.inherited(arguments);
      this.dialog = new Dialog({
        title: 'Add new concept',
        style: 'width: 1000px; min-height: 700px;'
        //onHide: lang.hitch(this, function() {
        //  this.parent._closeAddDialog();
        //})
      });
      this.dialog.closeText.innerHTML = '<i class="fa fa-times"></i>';
      this.dialog.set('content', this);

      domUtils.addOptionsToSelect(this.typeNode, {
        data: this.listController.getConceptTypes(),
        idProperty: 'value',
        labelProperty: 'label'
      });

      domUtils.addOptionsToSelect(this.schemeNode, {
        data: this.conceptSchemeController.conceptSchemeList,
        idProperty: 'id',
        labelProperty: 'name'
      });
      on(this.schemeNode, 'change', lang.hitch(this, function(evt) {
        this.updateScheme(evt.target.value);
      }));

      this.scheme = this.schemeNode.value;

      this._createLabelsTab();
      this._createNotesTab();
      this._createRelationsTab();
      this._createMatchesTab();
    },

    /**
     * Standaard widget functie
     */
    startup: function () {
      this.inherited(arguments);
      this.tabContainer.layout();
      this.dialog.resize();
    },

    /**
     * Toont het dialog
     */
    showDialog: function () {
      this.dialog.show();
      this.tabContainer.layout();
      this.dialog.resize();
    },

    updateScheme: function(newScheme) {
      this.scheme = newScheme;
      this.relationManager.setScheme(newScheme);
    },

    /**
     * Sluit het dialog
     * @private
     */
    _close: function () {

      this._reset();
      this.dialog.hide();
    },

    _saveConcept: function(evt) {
      evt ? evt.preventDefault() : null;
      var concept = {};

      concept.type = this.typeNode.value;
      concept.concept_scheme = this.schemeNode.value;

      // mixin tab data
      var labelData = this.labelManager.getData();
      lang.mixin(concept, labelData);
      console.log(labelData);

      var noteData = this.noteManager.getData();
      lang.mixin(concept, noteData);
      console.log(noteData);

      var relationData = this.relationManager.getData();
      lang.mixin(concept, relationData);
      console.log(relationData);

      var matchesData = this.matchesManager.getData();
      lang.mixin(concept, matchesData);
      console.log(matchesData);

      // emit save event
      this.emit('new.concept.save', {
        concept: concept,
        schemeId: this.schemeNode.value
      });
    },

    _cancel: function(evt) {
      evt ? evt.preventDefault() : null;
      this._close();
    },

    _reset: function() {
      this.schemeNode.selectedIndex = 0;
      this.typeNode.selectedIndex = 0;
      this.labelManager.reset();
      this.noteManager.reset();
      this.relationManager.reset();
      this.matchesManager.reset();
    },

    _createLabelsTab: function(concept) {
      this.languageController.getLanguageStore().fetch().then(lang.hitch(this, function(languages) {
        this.labelManager = new LabelManager({
          languageController: this.languageController,
          listController: this.listController,
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
          conceptSchemeController: this.conceptSchemeController,
          languageList: languages,
          scheme: this.scheme
        }, this.relationsNode);
        this.relationManager.startup();
        this.updateScheme(this.schemeNode.value);
      }));
    },

    _createMatchesTab: function(concept) {
      this.languageController.getLanguageStore().fetch().then(lang.hitch(this, function(languages) {
        this.matchesManager = new MatchesManager({
          languageController: this.languageController,
          listController: this.listController,
          conceptSchemeController: this.conceptSchemeController,
          languageList: languages,
          scheme: this.scheme,
          matchTypes: this.listController.getMatchTypes()
        }, this.matchesNode);
        this.matchesManager.startup();
      }));
    }
  });
});