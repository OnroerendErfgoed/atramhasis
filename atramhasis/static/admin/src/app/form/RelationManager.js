define([
        "dojo/_base/declare",
        "dojo/_base/array",
        "dojo/dom-construct",
        "dojo/query",
        "dojo/on",
        "dijit/Dialog",
	    "dijit/_WidgetBase",
	    "dijit/_TemplatedMixin",
        "dijit/form/Form",
        "dijit/form/Button",
        "dijit/form/NumberTextBox",
        "dojo/store/Memory",
        "dojo/store/Cache",
        "dojo/store/JsonRest",
        "dijit/tree/ObjectStoreModel",
        "dijit/Tree",
        "dojo/text!./templates/RelationManager.html"
	 ],
function(
    declare,
    arrayUtil,
    domConstruct,
    query,
    on,
    Dialog,
    WidgetBase,
    TemplatedMixin,
    Form, Button, NumberTextBox,
    Memory, Cache, JsonRest,
    ObjectStoreModel, Tree,
    template
) {
	return declare(
		"app/form/RelationManager",
		[WidgetBase, TemplatedMixin],
	{
        templateString: template,

        name: 'RelationManager',

        scheme: null,

        relationDialog: null,

        relations: [],

        buildRendering: function() {
            this.inherited(arguments);
        },

        postCreate: function() {
            this.inherited(arguments);
            var self = this;

            var form = new Form();
//            var myStore = new Memory({
//                data: [{"children": [{"children": [{"children": [{"children": [], "type": "concept", "id": "0.61.63.114", "label": "Halstatt", "concept_id": 114}, {"children": [], "type": "concept", "id": "0.61.63.115", "label": "Hilversum-cultuur", "concept_id": 115}, {"children": [], "type": "concept", "id": "0.61.63.116", "label": "La T\u00e8ne", "concept_id": 116}, {"children": [], "type": "concept", "id": "0.61.63.117", "label": "Nederrijnse grafheuvelcultuur", "concept_id": 117}, {"children": [], "type": "concept", "id": "0.61.63.119", "label": "Plainseaucultuur", "concept_id": 119}, {"children": [], "type": "concept", "id": "0.61.63.120", "label": "Rhin-Suisse-France Oriental", "concept_id": 120}, {"children": [], "type": "concept", "id": "0.61.63.121", "label": "urnenveldencultuur", "concept_id": 121}], "type": "collection", "id": "0.61.63", "label": "culturen uit de metaaltijden", "concept_id": 63}, {"children": [{"children": [], "type": "concept", "id": "0.61.62.64", "label": "acheuleaan", "concept_id": 64}, {"children": [], "type": "concept", "id": "0.61.62.65", "label": "ahrensburgiaan", "concept_id": 65}, {"children": [], "type": "concept", "id": "0.61.62.66", "label": "aurignaciaan", "concept_id": 66}, {"children": [], "type": "concept", "id": "0.61.62.67", "label": "creswelliaan", "concept_id": 67}, {"children": [], "type": "concept", "id": "0.61.62.68", "label": "enkelgrafcultuur", "concept_id": 68}, {"children": [], "type": "concept", "id": "0.61.62.69", "label": "federmesser", "concept_id": 69}, {"children": [], "type": "concept", "id": "0.61.62.82", "label": "gravettiaan", "concept_id": 82}, {"children": [], "type": "concept", "id": "0.61.62.87", "label": "groupe de Blicquy", "concept_id": 87}, {"children": [], "type": "concept", "id": "0.61.62.88", "label": "hamburgiaan", "concept_id": 88}, {"children": [], "type": "concept", "id": "0.61.62.89", "label": "hazendonkgroep", "concept_id": 89}, {"children": [], "type": "concept", "id": "0.61.62.91", "label": "klokbekercultuur", "concept_id": 91}, {"children": [], "type": "concept", "id": "0.61.62.93", "label": "lineaire bandkeramiek", "concept_id": 93}, {"children": [], "type": "concept", "id": "0.61.62.95", "label": "magdaleniaan", "concept_id": 95}, {"children": [], "type": "concept", "id": "0.61.62.97", "label": "michelsbergcultuur", "concept_id": 97}, {"children": [], "type": "concept", "id": "0.61.62.98", "label": "micoquiaan", "concept_id": 98}, {"children": [], "type": "concept", "id": "0.61.62.100", "label": "mousteriaan", "concept_id": 100}, {"children": [], "type": "concept", "id": "0.61.62.102", "label": "Rijnbekkengroep", "concept_id": 102}, {"children": [], "type": "concept", "id": "0.61.62.104", "label": "r\u00f6ssencultuur", "concept_id": 104}, {"children": [], "type": "concept", "id": "0.61.62.106", "label": "Seine-Oise-Marne", "concept_id": 106}, {"children": [], "type": "concept", "id": "0.61.62.108", "label": "steingroep", "concept_id": 108}, {"children": [], "type": "concept", "id": "0.61.62.109", "label": "swifterbantcultuur", "concept_id": 109}, {"children": [], "type": "concept", "id": "0.61.62.110", "label": "tardenoisiaan", "concept_id": 110}, {"children": [], "type": "concept", "id": "0.61.62.112", "label": "trechterbekercultuur", "concept_id": 112}, {"children": [], "type": "concept", "id": "0.61.62.113", "label": "vlaardingencultuur", "concept_id": 113}], "type": "collection", "id": "0.61.62", "label": "culturen uit de steentijd", "concept_id": 62}], "type": "collection", "id": "0.61", "label": "culturen", "concept_id": 61}, {"children": [{"children": [], "type": "concept", "id": "0.60.22", "label": "art deco", "concept_id": 22}, {"children": [], "type": "concept", "id": "0.60.30", "label": "art nouvea", "concept_id": 30}, {"children": [], "type": "concept", "id": "0.60.7", "label": "barok", "concept_id": 7}, {"children": [], "type": "concept", "id": "0.60.28", "label": "brutalisme", "concept_id": 28}, {"children": [], "type": "concept", "id": "0.60.8", "label": "classicerende barok", "concept_id": 8}, {"children": [], "type": "concept", "id": "0.60.10", "label": "classicisme", "concept_id": 10}, {"children": [], "type": "concept", "id": "0.60.31", "label": "cottagestijl", "concept_id": 31}, {"children": [], "type": "concept", "id": "0.60.11", "label": "empire", "concept_id": 11}, {"children": [], "type": "concept", "id": "0.60.4", "label": "gotiek", "concept_id": 4}, {"children": [], "type": "concept", "id": "0.60.27", "label": "high tech", "concept_id": 27}, {"children": [{"children": [], "type": "concept", "id": "0.60.23.24", "label": "expo-stijl", "concept_id": 24}], "type": "concept", "id": "0.60.23", "label": "modernisme", "concept_id": 23}, {"children": [{"children": [], "type": "concept", "id": "0.60.35.32", "label": "beaux-artsstijl", "concept_id": 32}, {"children": [], "type": "concept", "id": "0.60.35.29", "label": "eclecticisme", "concept_id": 29}, {"children": [], "type": "concept", "id": "0.60.35.34", "label": "neo-Egyptisch", "concept_id": 34}, {"children": [], "type": "concept", "id": "0.60.35.33", "label": "neo-empire", "concept_id": 33}, {"children": [], "type": "concept", "id": "0.60.35.16", "label": "neobarok", "concept_id": 16}, {"children": [], "type": "concept", "id": "0.60.35.18", "label": "neobyzantijns", "concept_id": 18}, {"children": [{"children": [], "type": "concept", "id": "0.60.35.12.36", "label": "second empire", "concept_id": 36}], "type": "concept", "id": "0.60.35.12", "label": "neoclassicisme", "concept_id": 12}, {"children": [], "type": "concept", "id": "0.60.35.13", "label": "neogotiek", "concept_id": 13}, {"children": [], "type": "concept", "id": "0.60.35.17", "label": "neomoors", "concept_id": 17}, {"children": [], "type": "concept", "id": "0.60.35.14", "label": "neorenaissance", "concept_id": 14}, {"children": [], "type": "concept", "id": "0.60.35.19", "label": "neorococo", "concept_id": 19}, {"children": [], "type": "concept", "id": "0.60.35.15", "label": "neoromaans", "concept_id": 15}], "type": "concept", "id": "0.60.35", "label": "neostijl", "concept_id": 35}, {"children": [], "type": "concept", "id": "0.60.21", "label": "neotraditioneel", "concept_id": 21}, {"children": [], "type": "concept", "id": "0.60.25", "label": "organische architectuur", "concept_id": 25}, {"children": [], "type": "concept", "id": "0.60.26", "label": "postmodernisme", "concept_id": 26}, {"children": [], "type": "concept", "id": "0.60.20", "label": "regionalisme", "concept_id": 20}, {"children": [], "type": "concept", "id": "0.60.5", "label": "renaissance", "concept_id": 5}, {"children": [], "type": "concept", "id": "0.60.9", "label": "rococo", "concept_id": 9}, {"children": [], "type": "concept", "id": "0.60.3", "label": "romaans", "concept_id": 3}, {"children": [{"children": [], "type": "concept", "id": "0.60.1.2", "label": "vakwerkbouw", "concept_id": 2}], "type": "concept", "id": "0.60.1", "label": "traditioneel", "concept_id": 1}], "type": "collection", "id": "0.60", "label": "stijlen", "concept_id": 60}], "type": "collection", "id": "0", "label": "Stijlen en culturen", "concept_id": 0}],
//                getChildren: function(object){
//                    return object.children || [];
//                }
//            });
            var myStore = new Cache(new JsonRest({
                //TODO: make url/schme dynamic. problem: form startup is on page start, so url contains null instead of [scheme]
                target:"/conceptschemes/" + this.scheme + "/tree",
                getChildren: function(object){
                    return object.children || [];
                },
                mayHaveChildren: function(object){
                    return (object.children && object.children.length>0)
                }
            }), new Memory());

            // Create the model
            var myModel = new ObjectStoreModel({
                store: myStore,
                query: {id: 0}
            });

            // Create the Tree.
            var myTree = new Tree({
                model: myModel,
                getIconClass: function(/*dojo.store.Item*/ item, /*Boolean*/ opened){
//                    console.log(item);
                    if (item.type=='collection'){
                        return (opened ? "dijitFolderOpened" : "dijitFolderClosed");
                    }else{
                        //return myStore.getValue(item, "type") + "Icon";
                        return "dijitLeaf";
                    }
                },
                getLabel: function(/*dojo.store.Item*/ item){
                    return item.label;
                },
                dndParams: ["onDndDrop","itemCreator","onDndCancel","checkAcceptance", "checkItemAcceptance", "dragThreshold", "betweenThreshold", "singular"],
                singular : true,
                openOnClick: true
            }).placeAt(form.containerNode);

            var addRelBtn = new Button({
                label: "add",
                type: "submit"
            }).placeAt(form.containerNode);

            this.relationDialog = new Dialog({
                content: form,
                title: "Choose concept"
            });
            form.startup();
            form.onSubmit =function (evt) {
                evt.preventDefault();
                console.log("form submit");
                var sel = myTree.selectedItems[0];
                this.reset();
                if (sel){
                    console.log("myTree.selectedItems " + sel.id);
                    var path = arrayUtil.map(myTree.get("path"), function(item){ return item.label; });
                    self._addRelation(sel.concept_id, path);
                    myTree.set('paths', []);//Deselect values from tree
                    self.relationDialog.hide();
                }
                return false;
            };

            new Button({
                label: "Manage relations",
                onClick: function(){
                    self.relationDialog.show();
                }
            }, this.relationButton)
        },

        _addRelation: function(relId, path){
            console.log("saving rel: " + relId + " - " + path);
            var found = arrayUtil.some(this.relations, function(item){
                return item.id == relId;
            });
            if (!found) {
                this.relations.push({id: relId, path: path});
                this._createRelationList();
                return true;
            }
            return false;
        },

        _createRelationList: function() {
            var relListNode = this.relationListNode;
            query("li", relListNode).forEach(domConstruct.destroy);
            arrayUtil.forEach(this.relations, function(rel){
                domConstruct.create("li", {
                    innerHTML: rel.id + "(" + rel.path + ")"
                }, relListNode);
            });
        },

        getRelations: function(){
            return arrayUtil.map(this.relations, function(item){ return item.id; });
        }
	});
});
