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
    "dijit/_Widget",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",

    "dojo/text!./templates/App.html",

    "dijit/form/ComboBox", "dijit/form/Button", "dijit/Dialog",

    "./FilteredGrid",
    "./ConceptDetail",
    "./ThesaurusCollection",
    "./ConceptForm",
//    "dojo/text!./templates/ConceptForm.html",

    "dijit/layout/ContentPane",
    "dijit/layout/TabContainer",
    "dijit/layout/BorderContainer"


], function(
    declare, on, topic, aspect, lang,

    Memory,
    dom,
    request,
    registry,
    FilteringSelect,
    _Widget,
    _TemplatedMixin,
    _WidgetsInTemplateMixin,

    template,

    ComboBox, Button, Dialog,

    FilteredGrid, ConceptDetail,
    ThesaurusCollection,
    ConceptForm,

    ContentPane, TabContainer
    ){
    return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {

        templateString: template,
        thesauri: null,
        currentScheme: null,

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

            var schemeFileteringSelect=new FilteringSelect({
                id: "schemeSelect",
                name: "scheme",
                store: new Memory({ data: this.thesauri.schemelist }),
                searchAttr: "id",
                placeHolder: 'select thesaurus'
            },"selectNode");

            var filteredGrid = new FilteredGrid({
                id: "conceptGrid"
            }, "filteredGridNode");
            filteredGrid.startup();

            //resize dgrid after resizing contentpane - should be automatic
            aspect.after(registry.byId("appMenu"), "resize", function() {
                filteredGrid.conceptGrid.resize();
            });

            var conceptDialog = new Dialog({
                id: 'conceptDialog',
                content:new ConceptForm(),
                title:"Add concept",
                style: "width: 500px"
            }).placeAt(document.body);


            conceptDialog.content.onFirstInit();
            conceptDialog.onCancel(conceptDialog.content.labelManager.clearAll());
            var tc = registry.byId("center");

            var cpwelcome = new ContentPane({
                title: "Welcome",
                content: "[welcome]"
            });
            tc.addChild(cpwelcome);
            tc.startup();


             var addConceptButton = new Button({
                label: "Add concept or collection",
                disabled:"disabled"
            }, "addConceptNode");
            on(schemeFileteringSelect, "change", function(e){

                if(e)
                {
                    console.log("on schemeCombo ", e);
                    self.currentScheme = e;
                    filteredGrid.setScheme(e);
                    addConceptButton.set('disabled',false);
                }
                else
                {
                      filteredGrid.ResetConceptGrid();
                      addConceptButton.set('disabled',true);
                }



            });



                  on(addConceptButton, "click", function(){
                console.log("on addConceptButton " + self.currentScheme);
                conceptDialog.content.init(self.currentScheme);
                conceptDialog.show();
            });

           schemeFileteringSelect.startup();

            topic.subscribe("concept.open", lang.hitch(this, function(conceptid, schemeid){
                var cp = registry.byId(schemeid + "_" + conceptid);
                if (cp){
                    tc.selectChild(cp);
                }
                else {
                    var thesaurus = self.thesauri.stores[schemeid];
                    thesaurus.get(conceptid).then(function(item){
                        console.log("treestore item: " + item);
                        console.log("create contentpane");
                        var concept = new ConceptDetail({
                            conceptid : item.id,
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
                            member_of: item.member_of
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

            topic.subscribe("concept.delete",function(conceptid, schemeid){
                console.log("concept.delete subscribe: " + conceptid + "(" + schemeid + ")");
                var thesaurus = self.thesauri.stores[schemeid];
                filteredGrid.conceptGrid.store.remove(conceptid)
                    .then(function(){
                        filteredGrid.conceptGrid.refresh();
                        var cp = registry.byId(schemeid + "_" + conceptid);
                        tc.removeChild(cp);
                        cp.destroyRecursive();
                     });
            });

            topic.subscribe("concept.edit",function(conceptid, schemeid){
                console.log("concept.edit subscribe: " + conceptid + "(" + schemeid + ")");
            });

            topic.subscribe("conceptform.submit", function(form){
                console.log("conceptform.submit subscribe");
                console.log(form);

                var rowToAdd = {
                    "type": form.ctype,
                    "labels": [
                        {
                            "type": "prefLabel",
                            "language": "nl",
                            "label": "test"
                        }
                    ],
                    "notes": [],
                    "broader": form.broader,
                    "narrower": form.narrower,
                    "related": form.related,
                    "members": form.members,
                    "member_of": form.member_of
                };
                filteredGrid.conceptGrid.store.add(rowToAdd)
                    .then(
                        function(){
                            filteredGrid.conceptGrid.refresh();
                            console.log("row added");
                            conceptDialog.content.show({
                                spinnerNode: false,
                                formNode: false,
                                successNode: true
                            });
                            conceptDialog && conceptDialog.resize();
                        },
                        function(error){
                            console.log("An error occurred: " + error);
                        }

                    );
            });

        }

    });
});