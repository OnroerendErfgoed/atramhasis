define([
    "dojo/_base/declare",
    "dojo/on",
    "dojo/topic",
    "dojo/_base/lang",
    "dojo/store/Memory",

    "dijit/registry",
    "dijit/_Widget",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",

    "dojo/text!./templates/App.html",

    "dijit/form/ComboBox",

    "./FilteredGrid",
    "./ConceptDetail",
    "./ThesaurusCollection",

    "dijit/layout/ContentPane",
    "dijit/layout/TabContainer",
    "dijit/layout/BorderContainer"


], function(
    declare, on, topic, lang,

    Memory,

    registry,
    _Widget,
    _TemplatedMixin,
    _WidgetsInTemplateMixin,

    template,

    ComboBox,

    FilteredGrid, ConceptDetail,
    ThesaurusCollection,

    ContentPane, TabContainer
    ){
    return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {

        templateString: template,
        thesauri: null,

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

            var schemeCombo = new ComboBox({
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

            var tc = new TabContainer({
                tabPosition: 'bottom'
            });
            var centerPane = registry.byId("center");
            centerPane.set("content", tc);

            var cpwelcome = new ContentPane({
                title: "Welcome",
                content: "[welcome]"
            });
            tc.addChild(cpwelcome);
            tc.startup();

            on(schemeCombo, "change", function(e){
                console.log("on ", e);
                filteredGrid.setScheme(e);
            });

            var self = this;
            topic.subscribe("conceptOpen", lang.hitch(this, function(concept){
                var schemeid = concept.scheme;
                var cp = registry.byId(schemeid + "_" + concept.id);
                if (cp){
                    tc.selectChild(cp);
                }
                else {
                    var thesaurus = self.thesauri.stores[schemeid];
                    thesaurus.get(concept.id).then(function(item){
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
                filteredGrid.conceptGrid.store.remove(conceptid).then(
                    function(){
                        filteredGrid.conceptGrid.refresh();
                        var cp = registry.byId(schemeid + "_" + conceptid);
                        tc.removeChild(cp);
                        cp.destroyRecursive();
                     });
            });
        }

    });
});