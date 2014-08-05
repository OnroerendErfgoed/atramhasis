define([
        "dojo/_base/declare",
        "dojo/_base/array",
        "dojo/dom-construct",
        "dojo/query",
        "dojo/on",
        "dojo/dom-style",
        "dijit/Dialog",
        "dijit/_WidgetBase",
        "dijit/_TemplatedMixin",
        "dijit/form/Button",
        "dojo/store/Memory",
        "dojo/store/Cache",
        "dojo/store/JsonRest",
        "dijit/tree/ObjectStoreModel",
        "dijit/Tree",
        "dojo/topic",
         "./ConceptDetailList",
        "dojo/text!./templates/RelationManager.html"
    ],
    function (declare, arrayUtil, domConstruct, query, on, domStyle, Dialog, WidgetBase, TemplatedMixin, Button, Memory, Cache, JsonRest, ObjectStoreModel, Tree,Topic,ConceptDetailList, template) {
        return declare(
            "app/form/RelationManager",
            [WidgetBase, TemplatedMixin],
            {
               templateString: template,
                name: 'RelationManager',
                title: 'Relations:',
                _scheme: null,
                _relations: null,
                EditRelationButton:null,

                buildRendering: function () {
                    this.inherited(arguments);
                },

                postCreate: function () {
                    this.inherited(arguments);
                    var self = this;
                    this._relations = [];
                   self.relationsList = new ConceptDetailList({ }, self.relationListNode);
                   self.EditRelationButton= new Button({
                        label:"Add "+ self.title,
                        showLabel: true,
                        iconClass: 'plusIcon',
                        onClick: function () {
                            var dlg = self._createDialog();
                            dlg.show();
                        }
                    }, this.relationButton)

                Topic.subscribe("relation.delete", function (relationId) {

                    self._removeRelation(relationId);

                    });
                },

                _addRelation: function (relId, lbl, path) {
                    console.log("saving rel: " + relId + " - " + lbl);
                    var found = arrayUtil.some(this._relations, function (item) {
                        return item.id == relId;
                    });
                    if (!found) {
                        this._relations.push({id: relId, label: lbl, path: path});
                        this._createNodeList();
                        return true;
                    }
                    return false;
                },
                _removeRelation: function (relationId) {
                    var self=this;
                    console.log("removing relation from list: " + relationId);
                    arrayUtil.forEach(self._relations,function(rel)

                        {
                            if(rel.id==relationId)
                            {
                              var position = arrayUtil.indexOf(self._relations, rel);
                              self._relations.splice(position, 1);
                            }
                        }

                    )
                },
                 _createNodeList: function () {
                 var self=this;
                 self.relationsList.buidList(self.relationsList.mapRelationsForList(self._relations), self.title, false,true);

                },

                _removeRelationFromList: function (rel) {
                    console.log("removing relation from list: " + rel.id);
                    var position = arrayUtil.indexOf(this._relations, rel);
                    this._relations.splice(position, 1);
                    this._createRelationList();
                },

                _createDialog: function () {
                    var self = this;

                    var dlg = new Dialog({
                        style: "width: 300px",
                        title: "Choose a concept or collection",
                        doLayout: true
                    });

                    var myStore = new Cache(new JsonRest({
                        target: "/conceptschemes/" + self._scheme + "/tree",
                        getChildren: function (object) {
                            return object.children || [];
                        }
                    }), new Memory());
                    var myModel = new ObjectStoreModel({
                        store: myStore,
                        mayHaveChildren: function (object) {
                            return (object.children && object.children.length > 0)
                        },
                        getRoot: function (onItem) {
                            //create artificial scheme root to support trees with multiple root items
                            var children = this.store.query(this.query);
                            var root = { concept_id: '-1', type: 'collection', label: self._scheme, id: '-1', children: children};
                            onItem(root);
                        }
                    });
                    var myTree = new Tree({
                        model: myModel,
                        showRoot: false,
                        getIconClass: function (/*dojo.store.Item*/ item, /*Boolean*/ opened) {
                            if (item.type == 'collection') {
                                return (opened ? "dijitFolderOpened" : "dijitFolderClosed");
                            } else {
                                return "dijitLeaf";
                            }
                        },
                        getLabel: function (/*dojo.store.Item*/ item) {
                            return item.label;
                        },
                        dndParams: ["onDndDrop", "itemCreator", "onDndCancel", "checkAcceptance", "checkItemAcceptance", "dragThreshold", "betweenThreshold", "singular"],
                        singular: true
                    }).placeAt(dlg.containerNode);
                    var actionBar = domConstruct.create("div", {
                        'class': "dijitDialogPaneActionBar",
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
                        if (sel) {
                            var path = arrayUtil.map(myTree.get("path"), function (item) {
                                return item.label;
                            });
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

                    on(dlg, "hide", function () {
                        dlg.destroyRecursive();
                    });

                    return dlg
                },

                reset: function (relationType) {
                    this._relations = [];
                    this._createNodeList();
                    var lab="Add "+relationType;
                    this.EditRelationButton.set("label",lab);
                    this.EditRelationButton.set("iconClass","plusIcon");
                },

                getRelations: function () {
                    return  arrayUtil.map(this._relations, function (item) {
                        return item.id;
                    });
                },

                setRelations: function (relations) {
                    this._relations = relations;
                    this._createNodeList();
                },

                close: function () {
                    domStyle.set(this.domNode, "display", "none");
                    this.reset();
                },

                open: function () {
                    domStyle.set(this.domNode, "display", "block");
                },

                setScheme: function (scheme) {
                    this._scheme = scheme;

                }
            });
    });
