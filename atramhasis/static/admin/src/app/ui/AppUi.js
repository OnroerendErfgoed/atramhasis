/**
 * Main application user interface.
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/fx',
  'dojo/_base/array',
  'dojo/dom-style',
  'dojo/topic',
  'dojo/on',
  'dojo/window',
  'dojo/router',
  'dojo/query',
  'dojo/string',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dijit/ConfirmDialog',
  'dojo/text!./templates/AppUi.html',
  'dojo/text!./templates/Help.html',
  'dijit/layout/ContentPane',
  'dijit/layout/TabContainer',
  'dijit/layout/LayoutContainer',
  '../utils/DomUtils',
  './widgets/SearchPane',
  './widgets/ConceptDetail',
  './widgets/SlideMenu',
  './dialogs/ManageConceptDialog',
  './dialogs/ManageLanguagesDialog',
  './dialogs/ManageProvidersDialog',
  './dialogs/ImportConceptDialog',
  './dialogs/MergeConceptDialog',
  './dialogs/ManageSchemeDialog',
  '../utils/ErrorUtils',
  'dojo/NodeList-manipulate'
], function (
  declare,
  lang,
  fx,
  array,
  domStyle,
  topic,
  on,
  wind,
  router,
  query,
  string,
  _WidgetBase,
  _TemplatedMixin,
  ConfirmDialog,
  template,
  helpTemplate,
  ContentPane,
  TabContainer,
  LayoutContainer,
  domUtils,
  SearchPane,
  ConceptDetail,
  SlideMenu,
  ManageConceptDialog,
  ManageLanguagesDialog,
  ManageProvidersDialog,
  ImportConceptDialog,
  MergeConceptDialog,
  ManageSchemeDialog,
  errorUtils
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    loadingContainer: null,
    staticAppPath: null,
    canCreateProviders: null,
    conceptSchemeController: null,
    conceptController: null,
    languageController: null,
    listController: null,
    providerController: null,
    _searchPane: null,
    _conceptContainer: null,
    _slideMenu: null,
    _manageConceptDialog: null,
    _manageLanguagesDialog: null,
    _manageProvidersDialog: null,
    _importConceptDialog: null,
    _mergeConceptDialog: null,
    _selectedSchemeId: null,

    /**
     * Standard widget function.
     * @public
     */
    postCreate: function () {
      this.inherited(arguments);
      console.debug('AppUi::postCreate');
      this._registerLoadingEvents();
      this._registerRoutes();
      this._createSlideMenu(this.menuContainerNode);

      this._manageConceptDialog = new ManageConceptDialog({
        parent: this,
        languageController: this.languageController,
        listController: this.listController,
        conceptSchemeController: this.conceptSchemeController,
        providerController: this.providerController
      });
      on(this._manageConceptDialog, 'new.concept.save', lang.hitch(this, function(evt) {
        this._saveNewConcept(this._manageConceptDialog, evt.concept, evt.schemeId);
      }));
      on(this._manageConceptDialog, 'concept.save', lang.hitch(this, function(evt) {
        this._saveConcept(this._manageConceptDialog, evt.concept, evt.schemeId);
      }));
      this._manageConceptDialog.startup();

      this._manageLanguagesDialog = new ManageLanguagesDialog({
        parentNode: this,
        languageController: this.languageController
      });
      this._manageLanguagesDialog.startup();

      this._manageProvidersDialog = new ManageProvidersDialog({
        parentNode: this,
        providerController: this.providerController,
        languageController: this.languageController
      });
      this._manageProvidersDialog.startup();

      this._importConceptDialog = new ImportConceptDialog({
        externalSchemeStore: this.conceptSchemeController.getExternalSchemeStore(),
        conceptSchemeController: this.conceptSchemeController
      });
      this._importConceptDialog.startup();
      on(this._importConceptDialog, 'concept.import', lang.hitch(this, function(evt) {
        this._createImportConcept(evt.schemeId, evt.concept);
      }));

      this._mergeConceptDialog = new MergeConceptDialog({
        conceptSchemeController: this.conceptSchemeController
      });
      this._mergeConceptDialog.startup();
      on(this._mergeConceptDialog, 'concept.merge', lang.hitch(this, function(evt) {
        this._createMergeConcept(evt.conceptUri, evt.concept, evt.schemeId);
      }));

      this._manageSchemeDialog = new ManageSchemeDialog({
        parent: this,
        languageController: this.languageController,
        listController: this.listController,
        conceptSchemeController: this.conceptSchemeController
      });
      this._manageSchemeDialog.startup();
      on(this._manageSchemeDialog, 'scheme.save', lang.hitch(this, function(evt) {
        this._saveConceptScheme(this._manageSchemeDialog, evt.scheme);
      }));

      on(window, 'resize', lang.hitch(this, function() { this._calculateHeight() }));
    },

    /**
     * Standard widget function.
     * @public
     */
    startup: function () {
      this.inherited(arguments);
      console.debug('AppUi::startup');

      var ui = this._buildInterface();
      ui.startup();
      this._searchPane.startup();
      this._slideMenu._slideOpen();
      this._hideLoading();

      router.startup('#');
    },

    /**
     * Hide the 'Loading'-overlay.
     * @public
     */
    _hideLoading: function () {
      var node = this.loadingContainer;
      fx.fadeOut({
        node: node,
        onEnd: function (node) {
          domStyle.set(node, 'display', 'none');
        },
        duration: 1000
      }).play();
    },

    /**
     * Show the 'Loading'-overlay.
     * @public
     */
    _showLoading: function (message) {
      if (!message) message = "";
      var node = this.loadingContainer;
      query(".loadingMessage", node).innerHTML(message);

      domStyle.set(node, 'display', 'block');
      fx.fadeIn({
        node: node,
        duration: 1
      }).play();
    },

    _buildInterface: function () {
      console.debug('AppUi::createView');

      this._calculateHeight();
      //main layout container
      var appContainer = new LayoutContainer({
        design: 'headline',
        id: 'appContainer'
      }, this.conceptContainerNode);

      //body of main layout
      this._container = new TabContainer({
        tabPosition: 'bottom',
        splitter: true
      });

      appContainer.addChild(new ContentPane({
        content: this._container,
        region: 'center',
        baseClass: 'appBody'
      }));
      this._createHelpTab(this._container);

      appContainer.startup();
      return appContainer;
    },

    _createHelpTab: function (tabContainer) {
      console.debug('AppUi::_createHelpTab');
      tabContainer.addChild(new ContentPane({
        tabId: 'help',
        title: 'Info',
        content: helpTemplate,
        closable: false
      }));
    },

    /**
     * Listen to events to show/hide the loading overlay
     * @private
     */
    _registerLoadingEvents: function () {
      this.own(
        topic.subscribe('standby.show',lang.hitch(this, function(evt){
          this._showLoading(evt.message);
        })),
        topic.subscribe('standby.stop',lang.hitch(this, function(){
          this._hideLoading();
        }))
      );
    },

    _registerRoutes: function () {

      router.register('/conceptschemes/:scheme/c/:id', lang.hitch(this, function(evt){
        if (!evt.params.id || !evt.params.scheme) { return; }
        this._openConcept(evt.params.id, evt.params.scheme);
        this._closeMenu();
        router.go('#');
      }));

      router.register('/conceptschemes/:schemeId', lang.hitch(this, function(evt){
        if (!evt.params.schemeId) { return; }
        this._openEditConceptScheme(evt.params.schemeId);
        this._closeMenu();
        router.go('#');
      }));

      router.register('/conceptschemes/:schemeId/', lang.hitch(this, function(evt){
        if (!evt.params.schemeId) { return; }
        this._openEditConceptScheme(evt.params.schemeId);
        this._closeMenu();
        router.go('#');
      }));
    },

    _createConcept: function(evt) {
      evt ? evt.preventDefault() : null;
      console.debug('AppUi::_createConcept');

      this._manageConceptDialog.showDialog(this._selectedSchemeId, null,  'add');
    },

    _createAddSubordinateArrayConcept: function(concept, schemeId) {
      var newConcept = {
        superordinates: [],
        type: 'collection'
      };
      newConcept.superordinates.push(concept);
      this._manageConceptDialog.showDialog(schemeId, newConcept, 'add');
    },

    _createAddNarrowerConcept: function(concept, schemeId) {
      var newConcept = {
        broader: [],
        type: 'concept'
      };
      newConcept.broader.push(concept);
      this._manageConceptDialog.showDialog(schemeId, newConcept, 'add');
    },

    _createAddMemberConcept: function(concept, schemeId) {
      var newConcept = {
        member_of: [],
        type: 'concept'
      };
      newConcept.member_of.push(concept);
      this._manageConceptDialog.showDialog(schemeId, newConcept, 'add');
    },

    _createImportConcept: function(schemeId, concept) {
      this.conceptSchemeController.getConcept(schemeId, concept.uri).then(lang.hitch(this, function(result) {
        var newConcept = result;
        this._manageConceptDialog.showDialog(this._selectedSchemeId, newConcept, 'add');
      }));
    },

    _createMergeConcept: function(conceptUri, concept, schemeId) {
      this._showLoading('Merging concepts..');
      this.conceptSchemeController.getMergeMatch(conceptUri).then(lang.hitch(this, function (match) {
        var labelsToMerge = match.labels;
        var notesToMerge = match.notes;
        concept.labels = this._mergeLabels(concept.labels, labelsToMerge);
        concept.notes = this._mergeNotes(concept.notes, notesToMerge);

        this._manageConceptDialog.showDialog(schemeId, concept, 'edit');
      }), function (err) {
        topic.publish('dGrowl', err, {'title': "Error when looking up match", 'sticky': true, 'channel':'error'});
      }).always(lang.hitch(this, function() {
        this._hideLoading();
      }));
    },

    _importConcept  : function(evt) {
      evt.preventDefault();
      console.debug('AppUi::_importConcept');
      this._importConceptDialog.show();
    },

    _editLanguages: function (evt) {
      evt.preventDefault();
      console.debug('AppUi::_editLanguages');
      this._manageLanguagesDialog.show();
    },

    _editProviders: function () {
      console.debug('AppUi::_editProviders');
      this._manageProvidersDialog.show();
    },

    _editConceptScheme: function (evt) {
      evt.preventDefault();
      this._showLoading('Loading concept scheme..')
      // retrieve scheme and open dialog
      this.conceptSchemeController.getConceptScheme(this._selectedSchemeId).then(lang.hitch(this,
        function(schemeResult) {
          console.debug('AppUi::_editConceptScheme', schemeResult);
          this._manageSchemeDialog.showDialog(schemeResult, 'edit');
        }
      ), function (err) {
        console.error(err);
      }).always(lang.hitch(this, function() {
        this._hideLoading();
      }));
    },

    _openEditConceptScheme: function(schemeId) {
      this._showLoading('Loading concept scheme..')
      // retrieve scheme and open dialog
      this.conceptSchemeController.getConceptScheme(schemeId).then(lang.hitch(this,
        function(schemeResult) {
          console.debug('AppUi::_editConceptScheme', schemeResult);
          this._manageSchemeDialog.showDialog(schemeResult, 'edit');
        }
      ), function (err) {
        console.error(err);
      }).always(lang.hitch(this, function() {
        this._hideLoading();
      }));
    },

    _createSlideMenu: function(node) {
      this._slideMenu = new SlideMenu({
        overlayContainer: this.menuOverlayContainer
      }, node);
      this._slideMenu.startup();
      this._createSearchPane(this._slideMenu.menuNode);
    },

    _closeMenu: function(evt) {
      evt ? evt.preventDefault() : null;
      this._slideMenu._slideClose();
    },

    _toggleMenu: function(evt) {
      evt ? evt.preventDefault() : null;
      this._slideMenu._toggleMenu();
    },

    _openConcept: function(conceptId, scheme) {
      if (this._getTab(scheme + '_' + conceptId)) {
        this._openTab(this._getTab(scheme + '_' + conceptId));
        return;
      }
      this._showLoading('Loading concept..');
      this.conceptController.getConcept(scheme, conceptId).then(
        lang.hitch(this, function (data) {
          var conceptDetail = new ConceptDetail({
            concept: data,
            conceptId: conceptId,
            conceptLabel: data.label,
            scheme: scheme,
            languageController: this.languageController,
            listController: this.listController,
            conceptSchemeController: this.conceptSchemeController
          });
          on(conceptDetail, 'concept.save', lang.hitch(this, function(evt) {
            this._saveConcept(conceptDetail, evt.concept, evt.schemeId);
          }));
          on(conceptDetail, 'concept.delete', lang.hitch(this, function(evt) {
            this._deleteConcept(conceptDetail, evt.concept, evt.schemeId);
          }));
          on(conceptDetail, 'concept.edit', lang.hitch(this, function(evt) {
            this._editConcept(conceptDetail, evt.concept, evt.schemeId);
          }))
          on(conceptDetail, 'concept.merge', lang.hitch(this, function(evt) {
            this._mergeConcept(conceptDetail, evt.concept, evt.schemeId);
          }))
          conceptDetail.startup();
          this._addTab(conceptDetail);
        })).always(lang.hitch(this, function() {
        this._hideLoading();
      }));
    },

    _createSearchPane: function (node) {
      this._searchPane = new SearchPane({
        conceptSchemeList: this.conceptSchemeController.conceptSchemeList,
        appUi: this
      }, node);

      on(this._searchPane, 'row-select', lang.hitch(this, function (evt) {
        console.debug('catch select event', evt);
        this._openConcept(evt.data.id, evt.scheme);
      }));

      on(this._searchPane, 'scheme.changed', lang.hitch(this, function (evt) {
        this._selectedSchemeId = evt.schemeId;
      }));

      on(this._searchPane, 'concept.create', lang.hitch(this, function (evt) {
        this._createConcept();
      }));

      on(this._searchPane, 'concept.edit', lang.hitch(this, function (evt) {
        this.conceptController.getConcept(this._selectedSchemeId, evt.conceptId).then(
          lang.hitch(this, function (data) {
            this._editConcept(null, data, this._selectedSchemeId);
          }));
      }));

      on(this._searchPane, 'concept.delete', lang.hitch(this, function (evt) {
        this.conceptController.getConcept(this._selectedSchemeId, evt.conceptId).then(
          lang.hitch(this, function (data) {
            this._deleteConcept(this._getTab(this._selectedSchemeId + '_' + data.id), data, this._selectedSchemeId);
          }));
      }));

      on(this._searchPane, 'concept.addnarrower', lang.hitch(this, function (evt) {
        this.conceptController.getConcept(this._selectedSchemeId, evt.conceptId).then(
          lang.hitch(this, function (data) {
            this._createAddNarrowerConcept(data, this._selectedSchemeId);
          }));
      }));

      on(this._searchPane, 'concept.addsubarray', lang.hitch(this, function (evt) {
        this.conceptController.getConcept(this._selectedSchemeId, evt.conceptId).then(
          lang.hitch(this, function (data) {
            this._createAddSubordinateArrayConcept(data, this._selectedSchemeId);
          }));
      }));

      on(this._searchPane, 'concept.addmember', lang.hitch(this, function (evt) {
        this.conceptController.getConcept(this._selectedSchemeId, evt.conceptId).then(
          lang.hitch(this, function (data) {
            this._createAddMemberConcept(data, this._selectedSchemeId);
          }));
      }));
    },

    /* Tab container functions*/
    /**
     * Opent een tab in de tabcontainer.
     * @param {Object} child Tab die wordt geopend
     */
    _openTab: function(child) {
      this._container.selectChild(child);
    },

    /**
     * Sluit een tab in de tabcontainer en verwijdert de content uit de DOM.
     * @param {Object} child Tab die wordt gesloten
     */
    _closeTab: function(child) {
      console.debug('AppUi::_closeTab ', child.tabId);
      this._container.removeChild(child);
      child.destroyRecursive();
    },

    /**
     * Zoekt een tab en geeft die terug
     * @param {string} tabId ID van de tab
     * @returns {Contentpane} de gevonden tab of null
     * @private
     */
    _getTab: function(tabId) {
      var tabs = array.filter(this._container.getChildren(), function (tab) {
        return tab.tabId === tabId;
      });

      if(tabs.length > 0) {
        return tabs[0];
      }
      else {
        return null;
      }
    },

    /**
     * Voegt een nieuwe tab toe in de tabcontainer.
     * @param {Object} content Content die wordt toegevoegd in de tab.
     */
    _addTab: function(content) {
      var tab = content;
      tab.tabId = content.scheme + '_' + content.conceptId;
      tab.title = string.escape(content.conceptLabel);
      tab.closable = true;
      tab.onClose = lang.hitch(this, function() {
        this._closeTab(tab);
      });
      this._container.addChild(tab);
      this._container.selectChild(tab);
    },
    /*end tabcontainer*/

    _calculateHeight: function () {
      var win = wind.getBox();
      var footerheight = 30;
      var headerheight = 60;
      domStyle.set(this.appContentContainer, 'height', win.h - footerheight - headerheight + 'px');
      if (this._container) {
        this._container.resize();
      }
    },

    _editConcept: function(view, concept, schemeId) {
      console.debug('AppUi::_editConcept');
      this._manageConceptDialog.showDialog(schemeId, concept, 'edit');
    },

    _mergeConcept: function(view, concept, schemeId) {
      if (concept.matches) {
        this._mergeConceptDialog.show(concept, schemeId);
      }
    },

    _deleteConcept: function(view, concept, schemeId) {
      var content = '<p style="font-size: 15px;">Are you sure you want to remove <strong>'+ concept.label +
        '</strong> (ID: ' + concept.id + ') from scheme <strong>' + schemeId + '</strong>?</p>';
      var confirmationDialog = new ConfirmDialog({
        title: 'Delete concept',
        content: content,
        baseClass: 'confirm-dialog'
      });
      query('.dijitButton', confirmationDialog.domNode).addClass('button tiny');
      confirmationDialog.closeText.innerHTML = '<i class="fa fa-times"></i>';

      on(confirmationDialog, 'close', function() {
        confirmationDialog.destroy();
      });
      on(confirmationDialog, 'execute', lang.hitch(this, function () {
        this._showLoading('Removing concept..');
        this.conceptController.deleteConcept(concept, schemeId).then(
          lang.hitch(this, function(result) {
            console.debug('delete concept results', result);
            if (view) {
              this._closeTab(view);
            }
          }),
          lang.hitch(this, function (error) {
            console.error('delete concept error', error);
            var parsedError = errorUtils.parseError(error);
            topic.publish('dGrowl', parsedError.message, {
              'title': parsedError.title,
              'sticky': true,
              'channel': 'error'
            });
          })
        ).always(lang.hitch(this, function() {
          this._hideLoading();
        }));
      }));

      confirmationDialog.show();
    },

    _saveConcept: function(view, concept, schemeId) {
      console.debug('ConceptContainer::_saveConcept', concept);

      this._showLoading('Saving concept..');
      this.conceptController.saveConcept(concept, schemeId, 'PUT').then(lang.hitch(this, function(res) {
        // save successful
        view._close();
        var tab = this._getTab(schemeId + '_' + concept.id);
        this._closeTab(tab);
        this._openConcept(res.id, schemeId);
        this._searchPane.reload();
        topic.publish('dGrowl', 'The concept was successfully saved.', {
          'title': 'Save successful',
          'sticky': false,
          'channel': 'info'
        });
      }), function(err) {
        var parsedError = errorUtils.parseError(err);
        topic.publish('dGrowl', parsedError.message, {
          'title': parsedError.title,
          'sticky': true,
          'channel': 'error'
        });
      }).always(lang.hitch(this, function() {
        this._hideLoading();
      }));
    },

    _saveNewConcept: function(view, concept, schemeId) {
      this._showLoading('Saving concept..');
      this.conceptController.saveConcept(concept, schemeId, 'POST').then(lang.hitch(this, function(res) {
        // save successful
        view._close();
        this._openConcept(res.id, schemeId);
        this._searchPane.reload();
        topic.publish('dGrowl', 'The concept was successfully saved.', {
          'title': 'Save successful',
          'sticky': false,
          'channel': 'info'
        });
      }), function(err) {
        var parsedError = errorUtils.parseError(err);
        topic.publish('dGrowl', parsedError.message, {
          'title': parsedError.title,
          'sticky': true,
          'channel': 'error'
        });
      }).always(lang.hitch(this, function() {
        this._hideLoading();
      }));
    },

    _saveConceptScheme: function(view, scheme) {
      this._showLoading('Saving concept scheme..');
      this.conceptSchemeController.editConceptScheme(scheme).then(lang.hitch(this, function(res) {
        view._close();
        topic.publish('dGrowl', 'The concept scheme was successfully saved.', {
          'title': 'Save successful',
          'sticky': false,
          'channel': 'info'
        });
      }), function(err) {
        var parsedError = errorUtils.parseError(err);
        topic.publish('dGrowl', parsedError.message, {
          'title': parsedError.title,
          'sticky': true,
          'channel': 'error'
        });
      }).always(lang.hitch(this, function() {
        this._hideLoading();
      }));
    },

    _closeEditDialog: function() {
      if (this._editDialog) {
        this._editDialog._close();
        this._editDialog.destroyRecursive();
      }
    },

    _mergeLabels: function (currentLabels, labelsToMerge) {
      var mergedLabels = currentLabels;
      array.forEach(labelsToMerge, function(labelToMerge) {
        if (!this._containsLabel(currentLabels, labelToMerge)) {
          mergedLabels.push(this._verifyPrefLabel(mergedLabels, labelToMerge));
        }
      }, this);
      return mergedLabels;
    },

    _containsLabel: function (labels, labelToSearch) {
      return array.some(labels, function(label) {
        return label.label === labelToSearch.label
          && label.language === labelToSearch.language
          && label.type === labelToSearch.type;
      })
    },

    _verifyPrefLabel: function (labels, labelToMerge) {
      if (labelToMerge.type === 'prefLabel' && this._containsPrefLabelOfSameLanguage(labels, labelToMerge)) {
        labelToMerge.type = 'altLabel';
      }
      return labelToMerge;
    },

    _containsPrefLabelOfSameLanguage: function (labels, labelToSearch) {
      return array.some(labels, function(label) {
        return label.type === 'prefLabel'
          && label.language === labelToSearch.language;
      })
    },

    _mergeNotes: function (currentNotes, notesToMerge) {
      var mergedNotes = currentNotes;
      array.forEach(notesToMerge, function(noteToMerge) {
        if (!this._containsNote(currentNotes, noteToMerge)) {
          mergedNotes.push(noteToMerge);
        }
      }, this);
      return mergedNotes;
    },

    _containsNote: function (notes, noteToSearch) {
      return array.some(notes, function(note) {
        return note.note === noteToSearch.note
          && note.language === noteToSearch.language
          && note.type === noteToSearch.type;
      })
    }
  });
});
