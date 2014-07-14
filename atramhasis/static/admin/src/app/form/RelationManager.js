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
    Form, Button,
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

        title: 'Relations:',

        scheme: null,

        relations: [],

        buildRendering: function() {
            this.inherited(arguments);
        },

        postCreate: function() {
            this.inherited(arguments);
            var self = this;

            this.relationLabel.innerHTML = this.title;

            new Button({
                label: "Add relation",
                showLabel :false,
                iconClass: 'plusIcon',
                onClick: function(){
                    var dlg = self._createDialog();
                    dlg.show();
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

        _createDialog: function() {
            var self = this;

            var form = new Form();

            console.log("SCHEME in dialog: " + self.scheme);
            var myStore = new Cache(new JsonRest({
                target:"/conceptschemes/" + self.scheme + "/tree",
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

            var dlg = new Dialog({
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
                    dlg.hide();
                }
                return false;
            };

            on(dlg, "hide", function(){
                dlg.destroyRecursive();
            });

            return dlg
        },

        getRelations: function(){
            return arrayUtil.map(this.relations, function(item){ return item.id; });
        }
	});
});
