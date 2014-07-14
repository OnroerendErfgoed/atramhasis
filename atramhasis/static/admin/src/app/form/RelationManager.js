define([
        "dojo/_base/declare",
        "dojo/_base/array",
        "dojo/dom-construct",
        "dojo/query",
        "dojo/on",
        "dijit/Dialog",
	    "dijit/_WidgetBase",
	    "dijit/_TemplatedMixin",
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
    Button,
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

        _relations: null,

        buildRendering: function() {
            this.inherited(arguments);
        },

        postCreate: function() {
            this.inherited(arguments);
            var self = this;
            this._relations = [];

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

        _addRelation: function(relId, lbl, path){
            console.log("saving rel: " + relId + " - " + lbl);
            var found = arrayUtil.some(this._relations, function(item){
                return item.id == relId;
            });
            if (!found) {
                this._relations.push({id: relId, label: lbl, path: path});
                this._createRelationList();
                return true;
            }
            return false;
        },

        _createRelationList: function() {
            var self = this;
            var relListNode = this.relationListNode;
            query("li", relListNode).forEach(domConstruct.destroy);
            arrayUtil.forEach(this._relations, function(rel){
                var li = domConstruct.create("li", {
                    title: rel.path
                }, relListNode);

                var span = domConstruct.create("span", {
                    innerHTML: rel.label + " <em>(" + rel.id + ")</em>"
                }, li);

                var btn = new Button({
                    label: "remove this relation",
                    showLabel :false,
                    iconClass: 'minIcon',
                    onClick: function(){
                        self._removeRelationFromList(rel);
                    }
                }).placeAt(li);
            });
        },

        _removeRelationFromList: function(rel){
            console.log("removing relation from list: " + rel.id);
            var position = arrayUtil.indexOf(this._relations, rel);
            this._relations.splice(position, 1);
            this._createRelationList();
        },

        _createDialog: function() {
            var self = this;

            var dlg = new Dialog({
                style: "width: 300px",
                title: "Choose a concept or collection",
                doLayout: true
            });

            var myStore = new Cache(new JsonRest({
                target:"/conceptschemes/" + self.scheme + "/tree",
                getChildren: function(object){
                    return object.children || [];
                }
            }), new Memory());
            var myModel = new ObjectStoreModel({
                store: myStore,
                query: {id: 0},
                mayHaveChildren: function(object){
                    return (object.children && object.children.length > 0)
                }
            });
            var myTree = new Tree({
                model: myModel,
                getIconClass: function(/*dojo.store.Item*/ item, /*Boolean*/ opened){
                    if (item.type=='collection'){
                        return (opened ? "dijitFolderOpened" : "dijitFolderClosed");
                    }else{
                        return "dijitLeaf";
                    }
                },
                getLabel: function(/*dojo.store.Item*/ item){
                    return item.label;
                },
                dndParams: ["onDndDrop","itemCreator","onDndCancel","checkAcceptance", "checkItemAcceptance", "dragThreshold", "betweenThreshold", "singular"],
                singular : true
            }).placeAt(dlg.containerNode);
//            myTree.onOpen = function(){
//                dlg.resize();
//            };
//            myTree.onClose = function(){
//                dlg.resize();
//            };

            var actionBar = domConstruct.create("div", {
                class: "dijitDialogPaneActionBar",
                width: "300px"
            }, dlg.containerNode);

            var addBtn = new Button({
                "label": "Add"
            }).placeAt(actionBar);
            var cancelBtn = new Button({
                "label": "Cancel"
            }).placeAt(actionBar);

            addBtn.onClick = function () {
                var sel = myTree.selectedItems[0];
                if (sel){
                    var path = arrayUtil.map(myTree.get("path"), function(item){ return item.label; });
                    self._addRelation(sel.concept_id, sel.label, path);
                    dlg.hide();
                }
                else {
                    alert("Nothing is selected");
                }
            };
            cancelBtn.onClick = function () {
                dlg.hide();
            };

            on(dlg, "hide", function(){
                dlg.destroyRecursive();
            });

            return dlg
        },

        getRelations: function(){
            return arrayUtil.map(this._relations, function(item){ return item.id; });
        },

        setRelations: function(relations){
            console.log("todo");
        }
	});
});
