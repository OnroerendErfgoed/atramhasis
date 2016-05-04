define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/topic',
  'dojo/dom-attr',
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
  'dojo/text!./templates/ManageConceptDialog.html',
  'dijit/layout/TabContainer',
  'dijit/layout/ContentPane'
], function (
  declare,
  lang,
  topic,
  domAttr,
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
    concept: null,
    scheme: null,
    languageController: null,
    listController: null,
    conceptSchemeController: null,
    _mode: 'add',

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
      on(this.typeNode, 'change', lang.hitch(this, function(evt) {
        this._toggleMatches(evt.target.value);
        this._toggleRelations(evt.target.value);
      }));

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
    showDialog: function (scheme, concept) {
      if (scheme) {
        this.schemeNode.value = scheme;
        this.updateScheme(scheme);
        this.dialog.set('title', 'Add new concept or collection');
        domAttr.set(this.schemeNode, 'disabled', false);

        if (concept) {
          this._mode = 'edit';
          this.dialog.set('title', 'Edit <strong>' + concept.label + '</strong>');
          domAttr.set(this.schemeNode, 'disabled', true);
          this.relationManager.setConcept(concept);
          this.labelManager.setConcept(concept);
          this.noteManager.setConcept(concept);
          this.matchesManager.setConcept(concept);
          this.concept = concept;
        }
      }
      this.dialog.show();
      this.tabContainer.selectChild(this.tabLabels);
      this.tabContainer.layout();
      this.dialog.resize();
    },

    updateScheme: function(newScheme) {
      this.scheme = newScheme;
      this.relationManager.setScheme(newScheme);
    },

    _toggleMatches: function(type) {
      if (type === 'collection') {
        this.tabMatches.set('disabled', true);
        if (this.tabContainer.selectedChildWidget === this.tabMatches) {
          this.tabContainer.selectChild(this.tabLabels);
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

      this._reset();
      this.dialog.hide();
    },

    _saveConcept: function(evt) {
      evt ? evt.preventDefault() : null;
      var concept = {};

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

      if (this._mode === 'add') {
        // emit save event
        this.emit('new.concept.save', {
          concept: concept,
          schemeId: this.schemeNode.value
        });
      } else {
        this.emit('concept.save', {
          concept: concept,
          schemeId: this.schemeNode.value
        });
      }
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
          languageList: languages,
          scheme: this.scheme,
          concept: concept,
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
          concept: concept,
          matchTypes: this.listController.getMatchTypes()
        }, this.matchesNode);
        this.matchesManager.startup();
      }));
    }
  });
});