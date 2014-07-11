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
    Memory, ObjectStoreModel, Tree,
    template
) {
	return declare(
		"app/form/RelationManager",
		[WidgetBase, TemplatedMixin],
	{
        templateString: template,

        name: 'RelationManager',

        relationDialog: null,

        relations: [],

        buildRendering: function() {
            this.inherited(arguments);
        },

        postCreate: function() {
            this.inherited(arguments);
            var self = this;

            var form = new Form();
            var myStore = new Memory({
                data: [
                    { id: 'world', name:'The earth', type:'planet', population: '6 billion'},
                    { id: 'AF', name:'Africa', type:'continent', population:'900 million', area: '30,221,532 sq km',
                            timezone: '-1 UTC to +4 UTC', parent: 'world'},
                        { id: 'EG', name:'Egypt', type:'country', parent: 'AF' },
                        { id: 'KE', name:'Kenya', type:'country', parent: 'AF' },
                            { id: 'Nairobi', name:'Nairobi', type:'city', parent: 'KE' },
                            { id: 'Mombasa', name:'Mombasa', type:'city', parent: 'KE' },
                        { id: 'SD', name:'Sudan', type:'country', parent: 'AF' },
                            { id: 'Khartoum', name:'Khartoum', type:'city', parent: 'SD' },
                    { id: 'AS', name:'Asia', type:'continent', parent: 'world' },
                        { id: 'CN', name:'China', type:'country', parent: 'AS' },
                        { id: 'IN', name:'India', type:'country', parent: 'AS' },
                        { id: 'RU', name:'Russia', type:'country', parent: 'AS' },
                        { id: 'MN', name:'Mongolia', type:'country', parent: 'AS' },
                    { id: 'OC', name:'Oceania', type:'continent', population:'21 million', parent: 'world'},
                    { id: 'EU', name:'Europe', type:'continent', parent: 'world' },
                        { id: 'DE', name:'Germany', type:'country', parent: 'EU' },
                        { id: 'FR', name:'France', type:'country', parent: 'EU' },
                        { id: 'ES', name:'Spain', type:'country', parent: 'EU' },
                        { id: 'IT', name:'Italy', type:'country', parent: 'EU' },
                    { id: 'NA', name:'North America', type:'continent', parent: 'world' },
                    { id: 'SA', name:'South America', type:'continent', parent: 'world' }
                ],
                getChildren: function(object){
                    return this.query({parent: object.id});
                }
            });

            // Create the model
            var myModel = new ObjectStoreModel({
                store: myStore,
                query: {id: 'world'}
            });

            // Create the Tree.
            var tree = new Tree({
                model: myModel,
                getIconClass: function(/*dojo.store.Item*/ item, /*Boolean*/ opened){
                    console.log(item);
                    if (item.type=='continent'){
                        return (opened ? "dijitFolderOpened" : "dijitFolderClosed");
                    }else{
                        //return myStore.getValue(item, "type") + "Icon";
                        return "dijitLeaf";
                    }
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
                var sel = tree.selectedItems[0];
                this.reset();
                if (sel){
                    console.log("tree.selectedItems " + sel.id);
                    self._addRelation(sel.id);
                    tree.set('paths', []);//Deselect values from tree
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

        _addRelation: function(relId){
            console.log("saving rel: " + relId);
            var found = arrayUtil.some(this.relations, function(item){
                return item == relId;
            });
            if (!found) {
                this.relations.push(relId);
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
                    innerHTML: rel
                }, relListNode);
            });
        },

        getRelations: function(){
            return this.relations;
        }
	});
});
