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
  'dojo/text!./templates/ConceptEditDialog.html',
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
    baseClass: 'concept-edit-dialog',
    concept: null,
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
        title: 'Edit <strong>' + this.concept.label + '</strong>',
        style: 'width: 1000px; min-height: 700px;',
        onHide: lang.hitch(this, function() {
          this.parent._closeEditDialog();
        })
      });
      this.dialog.closeText.innerHTML = '<i class="fa fa-times"></i>';
      this.dialog.set('content', this);

      domUtils.addOptionsToSelect(this.typeNode, {
        data: this.listController.getConceptTypes(),
        idProperty: 'value',
        labelProperty: 'label'
      });
      on(this.typeNode, 'change', lang.hitch(this, function(evt) {
        this._toggleMatches(evt.target.value);
        this._toggleRelations(evt.target.value);
      }));

      this._createLabelsTab(this.concept);
      this._createNotesTab(this.concept);
      this._createRelationsTab(this.concept);
      this._createMatchesTab(this.concept);
    },

    /**
     * Standaard widget functie
     */
    startup: function () {
      this.inherited(arguments);
      if (this.concept) {
        this._setData(this.concept);
      }
      this.showDialog();
      this.tabContainer.layout();
      this.dialog.resize();
    },

    _setData: function(concept) {
      this.schemeNode.value = this.scheme;
      this.typeNode.value = this.concept.type;
      this._toggleMatches(this.concept.type);
    },

    /**
     * Toont het dialog
     */
    showDialog: function () {
      this.tabContainer.layout();
      this.dialog.show();
      this.dialog.resize();
    },

    _toggleMatches: function(type) {
      if (type === 'collection') {
        this.tabMatches.set('disabled', true);
        if (this.tabContainer.selectedChildWidget === this.tabMatches) {
          this.tabContainer.selectChild(this.tabLabels)
        }
      } else {
        this.tabMatches.set('disabled', false);
      }
    },

    _toggleRelations: function(type) {
      if (type === 'collection') {
        this.relationManager.setCollectionTypes();
      } else {
        this.relationManager.setConceptTypes();
      }
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
      var concept = {};

      // set concept specific fields
      if (this.concept) {
        concept.id = this.concept.id;
        concept.uri = this.concept.uri;
        /* jshint -W106 */
        concept.concept_scheme = this.scheme;
        /* jshint +W106 */
      }

      concept.type = this.typeNode.value;

      // mixin tab data
      var labelData = this.labelManager.getData();
      lang.mixin(concept, labelData);

      var noteData = this.noteManager.getData();
      lang.mixin(concept, noteData);

      var relationData = this.relationManager.getData();
      lang.mixin(concept, relationData);

      if (concept.type !== 'collection') {
        var matchesData = this.matchesManager.getData();
        lang.mixin(concept, matchesData);
      }

      // emit save event
      this.emit('concept.save', {
        concept: concept,
        schemeId: this.scheme
      });

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
          conceptSchemeController: this.conceptSchemeController,
          concept: concept,
          languageList: languages,
          scheme: this.scheme
        }, this.relationsNode);
        this.relationManager.startup();
      }));
    },

    _createMatchesTab: function(concept) {
      this.languageController.getLanguageStore().fetch().then(lang.hitch(this, function(languages) {
        this.matchesManager = new MatchesManager({
          languageController: this.languageController,
          listController: this.listController,
          conceptSchemeController: this.conceptSchemeController,
          concept: concept,
          languageList: languages,
          scheme: this.scheme,
          matchTypes: this.listController.getMatchTypes()
        }, this.matchesNode);
        this.matchesManager.startup();
      }));
    }
  });
});