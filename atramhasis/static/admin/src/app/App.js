define([
    "dojo/_base/declare",
    "dojo/on",
    "dojo/topic",
    "dojo/aspect",
    "dojo/_base/lang",
    "dojo/store/Memory",
    "dojo/dom",
    "dojo/request",
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
    "./ImportForm",
    "./ExternalSchemeService",
    "./ExternalSchemeForm",
    "dijit/layout/ContentPane",
    "dijit/layout/TabContainer",
    "dijit/layout/BorderContainer"


], function (declare, on, topic, aspect, lang, Memory, dom, request, registry, FilteringSelect, MenuItem,
             _Widget, _TemplatedMixin, _WidgetsInTemplateMixin, template, array, ComboBox, Button, Dialog,
             FilteredGrid, ConceptDetail, ThesaurusCollection, ConceptForm, ImportForm, ExternalSchemeService,
             ExternalSchemeForm, ContentPane, TabContainer) {
    return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {

        templateString: template,
        thesauri: null,
        currentScheme: null,
        externalSchemeService: null,
        externalSchemeForm: null,

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
        },

        startup: function () {
            this.inherited(arguments);
            console.log('startup', arguments);
            var self = this;

            this.externalSchemeService = new ExternalSchemeService({
                thesauri: this.thesauri
            });

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
                externalSchemeService: this.externalSchemeService

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

            console.log("startup conceptDialog");

//            var importForm = new ImportForm({externalSchemeStore: this.thesauri.externalSchemeStore});
//
//            var importDialog = new Dialog({
//                id: 'importDialog',
//                content: importForm
//
//            }).placeAt(document.body);

//            on(importForm, "cancel", function () {
//                importDialog.hide();
//            });
//
//            on(importDialog, "hide", function () {
//                importForm.reset();
//            });

//            console.log("startup importDialog");

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

            this.externalSchemeForm = new ExternalSchemeForm({
                externalSchemeService: this.externalSchemeService
            });
            this.externalSchemeForm.startup();

            on(this.externalSchemeForm, 'select', function (evt) {
                if (evt.concept && evt.concept.uri){
                    self._importConcept(conceptForm, conceptDialog, evt.concept.uri);
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
                        console.log("treestore item: " + item);
                        console.log("create contentpane");
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
                            matchUris: item.matches,
                            externalSchemeService: self.externalSchemeService
                        });
                        cp = new ContentPane({
                            id: schemeid + "_" + item.id,
                            title: item.label,
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
                    });
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
            topic.subscribe("concept.addNarrower", function (conceptid, type, label) {
                    console.log("concept.addMemberOf subscribe: " + label + " " + conceptid + " " + label + " (" + self.currentScheme + ")");

                    var thesaurus = self.thesauri.stores[self.currentScheme];

                    thesaurus.get(conceptid).then(function (item) {
                        var broader = [
                            {label: item.label, id: item.id, labels: item.labels, type: item.type, uri: item.uri}
                        ];
                        conceptForm.init(self.currentScheme);
                        conceptForm.addBroader(broader);
                        conceptDialog.set("title", "Add concept or collection to the " + type + " " + label);
                        conceptDialog.show();
                    });
                }
            );


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

                broader = array.map(form.broader, function(item){ return {"id": item}; });
                narrower = array.map(form.narrower, function(item){ return {"id": item}; });
                related = array.map(form.related, function(item){ return {"id": item}; });
                members = array.map(form.members, function(item){ return {"id": item}; });
                member_of = array.map(form.member_of, function(item){ return {"id": item}; });

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
                    "matches": form.matches
                };
                if (form.concept_id) {
                    filteredGrid.conceptGrid.store.put(rowToAdd, {id: form.concept_id})
                        .then(
                        function () {
                            console.log("row edited");
                            conceptDialog.hide();
                            alert("The concept or collection has been saved");
                            filteredGrid.conceptGrid.refresh();

                            //refresh Concept Detail widget.
                            self.thesauri.stores[self.currentScheme].get(form.concept_id).then(function (item) {
                                topic.publish("conceptDetail.refresh", item);
                            });
                        },
                        function (error) {
                            console.log("An error occurred: " + error);
                            alert("Can't add the concept or collection to the database. Please check if business rules are respected");
                        }
                    );
                }
                else {
                    filteredGrid.conceptGrid.store.add(rowToAdd)
                        .then(
                        function () {
                            console.log("row added");
                            conceptDialog.hide();
                            alert("The concept or collection has been added to the thesaurus");

                            filteredGrid.conceptGrid.refresh();
                        },
                        function (error) {
                            console.log("An error occurred: " + error);
                            alert("Can't add the concept or collection to the database. Please check if business rules are respected");
                        }
                    );
                }
            });

        },

        _createConcept: function (conceptForm, conceptDialog, Scheme) {
            conceptForm.init(Scheme);
            conceptDialog.set("title", "Add concept or collection");
            conceptDialog.show();
        },

        _importConcept: function (conceptForm, conceptDialog, concepturi) {
            var scheme = this.currentScheme;
            this.externalSchemeService.getConcept(concepturi).then(function(concept) {
                var clone = {
                    label: concept.label,
                    labels: concept.labels,
                    type: concept.type,
                    notes: concept.notes,
                    matches: {
                        exactMatch: [concepturi]
                    }
                };
                conceptForm.init(scheme, clone);
                conceptDialog.set("title", "Import concept or collection");
                conceptDialog.show();
            }, function(err){
                console.error(err);
            });
        }


    });
});