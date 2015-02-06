define([
    "dojo/_base/declare",
    "dojo/on",
    "dojo/topic",
    "dojo/aspect",
    "dojo/_base/lang",
    "dojo/store/Memory",
    "dojo/dom",
    "dojo/request",
    "dojo/json",
    "dojo/string",
    "dijit/registry",
    "dijit/form/FilteringSelect",
    "dijit/MenuItem",
    "dijit/_Widget",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "dojo/text!./templates/App.html",
    "dojo/_base/array",

    "dijit/form/ComboBox", "dijit/form/Button", "dijit/Dialog",

    "./FilteredGrid",
    "./ConceptDetail",
    "./ThesaurusCollection",
    "./ConceptForm",
    "./ExternalSchemeService",
    "./ExternalSchemeForm",
    "./LanguageManager",
    "dGrowl",
    "dijit/layout/ContentPane",
    "dijit/layout/TabContainer",
    "dijit/layout/BorderContainer"


], function (declare, on, topic, aspect, lang, Memory, dom, request, JSON, string, registry, FilteringSelect, MenuItem,
             _Widget, _TemplatedMixin, _WidgetsInTemplateMixin, template, array, ComboBox, Button, Dialog,
             FilteredGrid, ConceptDetail, ThesaurusCollection, ConceptForm, ExternalSchemeService,
             ExternalSchemeForm, LanguageManager, dGrowl, ContentPane, TabContainer) {
    return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {

        templateString: template,
        thesauri: null,
        currentScheme: null,
        externalSchemeService: null,
        externalSchemeForm: null,
        notificationController: null,
        languageManager: null,

        postMixInProperties: function () {
            this.inherited(arguments);

            console.log('postMixInProperties', arguments);
        },

        buildRendering: function () {
            this.inherited(arguments);

            console.log('buildRendering', arguments);
        },

        postCreate: function () {
            this.inherited(arguments);
            console.log('postCreate', arguments);
            this.thesauri = new ThesaurusCollection();

            this.notificationController = new dGrowl({
                'channels':[
                    {'name':'info','pos':3},
                    {'name':'error', 'pos':1},
                    {'name':'warn', 'pos':2}
                ]
            });
        },

        startup: function () {
            this.inherited(arguments);
            console.log('startup', arguments);
            var self = this;

            this.externalSchemeService = new ExternalSchemeService({
                thesauri: this.thesauri
            });

            this.languageManager = new LanguageManager({});

            var schemeFileteringSelect = new FilteringSelect({
                id: "schemeSelect",
                name: "scheme",
                store: new Memory({ data: this.thesauri.schemelist }),
                searchAttr: "id",
                placeHolder: 'select thesaurus'
            }, "selectNode");

            var filteredGrid = new FilteredGrid({
                id: "conceptGrid"
            }, "filteredGridNode");
            filteredGrid.startup();

            //resize dgrid after resizing contentpane - should be automatic
            aspect.after(registry.byId("appMenu"), "resize", function () {
                filteredGrid.conceptGrid.resize();
            });

            var conceptForm = new ConceptForm({
                thesauri: this.thesauri,
                externalSchemeService: this.externalSchemeService,
                languageStore: this.languageManager.languageStore
            });
            var conceptDialog = new Dialog({
                id: 'conceptDialog',
                content: conceptForm

            }).placeAt(document.body);

            on(conceptForm, "cancel", function () {
                conceptDialog.hide();
            });

            on(conceptDialog, "hide", function () {
                conceptForm.reset();
            });

            var tc = registry.byId("center");

            var cpwelcome = new ContentPane({
                title: "Welcome",
                content: "[welcome]"
            });
            tc.addChild(cpwelcome);
            tc.startup();

            //add "close all" option to tabs
            var menuBtn = registry.byId("center_tablist_Menu");
            if(menuBtn) {
                menuBtn.addChild(new MenuItem({
                    label: 'Close all',
                    onClick: function (evt) {
                        array.forEach(tc.getChildren(), function (tab) {
                            if (tab.closable) tc.closeChild(tab);
                        });
                    }
                }));
            }

            var addConceptButton = new Button({
                label: "Add concept or collection",
                disabled: "disabled"
            }, "addConceptNode");

            on(addConceptButton, "click", function () {

                console.log("on addConceptButton " + self.currentScheme);
                self._createConcept(conceptForm, conceptDialog, self.currentScheme);
            });

            var importConceptButton = new Button ({
                label: "Import concept or collection",
                disabled: "disabled"
            }, "importConceptNode");

            on(importConceptButton, "click", function () {
                self.externalSchemeForm.showDialog();
            });

            var manageLanguagesButton = new Button ({
                label: "Manage languages"
            }, "languageConceptNode");
            this._setupLanguageManager(manageLanguagesButton);

            this.externalSchemeForm = new ExternalSchemeForm({
                externalSchemeService: this.externalSchemeService
            });
            this.externalSchemeForm.startup();

            on(this.externalSchemeForm, 'select', function (evt) {
                if (evt.concept && evt.concept.uri && evt.scheme){
                    self._importConcept(conceptForm, conceptDialog, evt.concept.uri, evt.scheme);
                }
                else {
                    console.error('No valid URI.');
                }
            });

            on(schemeFileteringSelect, "change", function (e) {
                if (e) {
                    console.log("on schemeCombo ", e);
                    self.currentScheme = e;
                    filteredGrid.setScheme(e);
                    addConceptButton.set('disabled', false);
                    importConceptButton.set('disabled', false);
                }
                else {
                    filteredGrid.ResetConceptGrid();
                    addConceptButton.set('disabled', true);
                    importConceptButton.set('disabled', true);
                }
            });

            schemeFileteringSelect.startup();

            topic.subscribe("concept.open", lang.hitch(this, function (conceptid, schemeid) {
                var cp = registry.byId(schemeid + "_" + conceptid);
                if (cp) {
                    tc.selectChild(cp);
                }
                else {
                    var thesaurus = self.thesauri.stores[schemeid];
                    thesaurus.get(conceptid).then(function (item) {
                        console.log("create contentpane");
                        console.log(item);
                        var concept = new ConceptDetail({
                            conceptid: item.id,
                            label: item.label,
                            type: item.type,
                            uri: item.uri,
                            schemeid: schemeid,
                            labels: item.labels,
                            notes: item.notes,
                            narrower: item.narrower,
                            related: item.related,
                            broader: item.broader,
                            members: item.members,
                            member_of: item.member_of,
                            subordinate_arrays: item.subordinate_arrays,
                            superordinates: item.superordinates,
                            matchUris: item.matches,
                            externalSchemeService: self.externalSchemeService
                        });
                        cp = new ContentPane({
                            id: schemeid + "_" + item.id,
                            title: string.escape(item.label),
                            closable: true,
                            style: "padding: 0",
                            content: concept
                        });
                        tc.addChild(cp);
                        tc.selectChild(cp);
                    });
                }

            }));

            topic.subscribe("concept.delete", function (conceptid) {
                console.log("concept.delete subscribe: " + conceptid + "(" + self.currentScheme + ")");
                var thesaurus = self.thesauri.stores[self.currentScheme];
                filteredGrid.conceptGrid.store.remove(conceptid)
                    .then(function () {
                        filteredGrid.conceptGrid.refresh();
                        var cp = registry.byId(self.currentScheme + "_" + conceptid);
                        tc.removeChild(cp);
                        cp.destroyRecursive();
                    },
                    function (error) {
                        self._handleRemoveErrors(error);
                    }
                );
            });

            topic.subscribe("concept.edit", function (conceptid) {
                console.log("concept.edit subscribe: " + conceptid + "(" + self.currentScheme + ")");
                var thesaurus = self.thesauri.stores[self.currentScheme];
                thesaurus.get(conceptid).then(function (item) {
                    conceptForm.init(self.currentScheme, item);
                    conceptDialog.set("title", "Edit " + item.label);
                    conceptDialog.show();
                });
            });
            topic.subscribe("concept.addNarrower", function (conceptid, label) {
                    var thesaurus = self.thesauri.stores[self.currentScheme];

                    thesaurus.get(conceptid).then(function (item) {
                        var broader = [
                            {label: item.label, id: item.id, labels: item.labels, type: item.type, uri: item.uri}
                        ];
                        conceptForm.init(self.currentScheme);
                        conceptForm.addBroader(broader);
                        conceptForm.setType('concept');
                        conceptDialog.set("title", "Add narrower concept to '" + label + "'");
                        conceptDialog.show();
                    });
                }
            );

            topic.subscribe("concept.addSubordinateArray", function (conceptid, label) {
                var thesaurus = self.thesauri.stores[self.currentScheme];

                thesaurus.get(conceptid).then(function (item) {
                    var superordinate = [
                        {label: item.label, id: item.id, labels: item.labels, type: item.type, uri: item.uri}
                    ];
                    conceptForm.init(self.currentScheme);
                    conceptForm.addSuperordinate(superordinate);
                    conceptForm.setType('collection');
                    conceptDialog.set("title", "Add subordinate array to '" + label + "'");
                    conceptDialog.show();
                });
            });


            topic.subscribe("concept.addMemberOf", function (conceptid, type, label) {
                    console.log("concept.addMemberOf subscribe: " + label + " " + conceptid + " " + label + " (" + self.currentScheme + ")");

                    var thesaurus = self.thesauri.stores[self.currentScheme];

                    thesaurus.get(conceptid).then(function (item) {
                        var MemberOf = [
                            {label: item.label, id: item.id, labels: item.labels, type: item.type, uri: item.uri}
                        ];
                        conceptForm.init(self.currentScheme);
                        conceptForm.addMemberOf(MemberOf);
                        conceptDialog.set("title", "Add concept or collection to the " + type + " " + label);
                        conceptDialog.show();
                    });
                }
            );

            topic.subscribe("concept.create", function () {
                console.log("concept.create subscribe: ask to create a concept/collection from grid concept menu");
                self._createConcept(conceptForm, conceptDialog, self.currentScheme);
            });


            topic.subscribe("conceptform.submit", function (form) {
                console.log("conceptform.submit subscribe");
                console.log(form);

                var broader = array.map(form.broader, function(item){ return {"id": item}; });
                var narrower = array.map(form.narrower, function(item){ return {"id": item}; });
                var related = array.map(form.related, function(item){ return {"id": item}; });
                var members = array.map(form.members, function(item){ return {"id": item}; });
                var member_of = array.map(form.member_of, function(item){ return {"id": item}; });
                var subordinate_arrays = array.map(form.subordinate_arrays, function(item){ return {"id": item}; });
                var superordinates = array.map(form.superordinates, function(item){ return {"id": item}; });

                var rowToAdd = {
                    "id:": form.concept_id,
                    "type": form.ctype,
                    "labels": form.label,
                    "notes": form.note,
                    "broader": broader,
                    "narrower": narrower,
                    "related": related,
                    "members": members,
                    "member_of": member_of,
                    "subordinate_arrays": subordinate_arrays,
                    "superordinates": superordinates,
                    "matches": form.matches
                };
                if (form.concept_id) {
                    filteredGrid.conceptGrid.store.put(rowToAdd, {id: form.concept_id})
                        .then(
                        function () {
                            console.log("row edited");
                            conceptDialog.hide();
                            var message = "The " + rowToAdd.type + " has been saved";
                            topic.publish('dGrowl', message, {'title': "Success", 'sticky': false, 'channel':'info'});
                            filteredGrid.conceptGrid.refresh();

                            //refresh Concept Detail widget.
                            self.thesauri.stores[self.currentScheme].get(form.concept_id).then(function (item) {
                                topic.publish("conceptDetail.refresh", item);
                            });
                        },
                        function (error) {
                            self._handleSaveErrors(error);
                        }
                    );
                }
                else {
                    filteredGrid.conceptGrid.store.add(rowToAdd)
                        .then(
                        function () {
                            conceptDialog.hide();
                            var message = "The " + rowToAdd.type + " has been saved";
                            topic.publish('dGrowl', message, {'title': "Success", 'sticky': false, 'channel':'info'});
                            filteredGrid.conceptGrid.refresh();
                        },
                        function (error) {
                            self._handleSaveErrors(error);
                        }
                    );
                }
            });

            this.notificationController.addNotification("Atramhasis is up and running",{'channel':'info'});

        },

        _createConcept: function (conceptForm, conceptDialog, Scheme) {
            conceptForm.init(Scheme);
            conceptDialog.set("title", "Add concept or collection");
            conceptDialog.show();
        },

        _importConcept: function (conceptForm, conceptDialog, concepturi, importscheme) {
            var scheme = this.currentScheme;
            try {
                this.externalSchemeService.getConcept(importscheme, concepturi).then(function(concept) {
                    var clone = {
                        label: concept.label,
                        labels: concept.labels,
                        type: concept.type,
                        notes: concept.notes
                    };
                    if(concept.type != 'collection'){
                        clone.matches = {
                            exact: [concepturi]
                        }
                    }
                    conceptForm.init(scheme, clone);
                    conceptDialog.set("title", "Import concept or collection");
                    conceptDialog.show();
                }, function(err){
                    console.error(err);
                });
            } catch(err) {
                topic.publish('dGrowl', "", {'title': err, 'sticky': true, 'channel':'error'});
            }
        },

        _handleSaveErrors: function(error) {
            var errorJson = JSON.parse(error.responseText);
            var message = "";
            array.forEach(errorJson.errors, function (errorObj) {
                for (prop in errorObj) {
                    message += "-<em>";
                    message += prop;
                    message += "</em>: ";
                    message += errorObj[prop];
                    message += "<br>";
                }
            });
            topic.publish('dGrowl', message, {'title': errorJson.message, 'sticky': true, 'channel':'error'});
        },

        _handleRemoveErrors: function(error) {
            var errorJson = JSON.parse(error.responseText);
            var message = "Used in:";
            array.forEach(errorJson.referenced_in, function (reference) {
                message += "-";
                message += reference;
                message += "<br>";
            });
            topic.publish('dGrowl', message, {'title': errorJson.message, 'sticky': true, 'channel':'error'});
        },

        _setupLanguageManager: function (button) {
            var languageManager = this.languageManager;
            languageManager.startup();

            on(button, "click", function () {
                languageManager.showDialog();
            });

            on(languageManager, 'change', function (evt) {
                topic.publish('dGrowl', evt.message, {'title': evt.title, 'sticky': false, 'channel':'info'});
            });
            on(languageManager, 'error', function (evt) {
                topic.publish('dGrowl', evt.message, {'title': evt.title, 'sticky': true, 'channel':'error'});
            });

        }


    });
});
