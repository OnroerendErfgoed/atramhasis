define([
        "dojo/_base/declare",
        "dijit/Dialog",
        "dijit/_WidgetBase",
        "dijit/_TemplatedMixin",
        "dijit/form/Button",
        "dijit/form/Select",
        "dgrid/OnDemandGrid",
        "dijit/form/TextBox",
        "dojox/layout/TableContainer",
        "dojo/_base/lang",
        "dojo/dom-construct",
        "dojo/store/Memory",
        "dgrid/editor",
        "dgrid/extensions/ColumnHider",
        "dojo/_base/array",
        "dojo/on",
        "./ConceptDetailList",
        "dojo/text!./templates/LabelManager.html"

    ],
    function (declare, Dialog, WidgetBase, TemplatedMixin, Button, Select, OnDemandGrid, TextBox, TableContainer, lang, domConstruct, Memory, editor, ColumnHider, arrayUtil, on, ConceptDetailList, template) {
        return declare(
            "app/form/LabelManager",
            [WidgetBase, TemplatedMixin],
            {
                templateString: template,

                name: 'LabelManager',
                title: 'Labels:',
                labelGrid: null,
                titleLabel: null,
                LabelGridContent: null,
                languageComboBox: null,
                labelTypeComboBox: null,
                prefLanguage: null,
                labels: null,
                tempLabels: null,//this variable is used to recover the labels if user delete a label and then press on the cancel button
                EditLabelButton: null,
                languageStore: null,

                buildRendering: function () {
                    this.inherited(arguments);
                },
                postCreate: function () {
                    this.inherited(arguments);
                    var self = this;
                    //noinspection CommaExpressionJS

                    self.EditLabelButton = new Button({
                        label: "Add Labels",
                        showLabel: true,
                        iconClass: 'plusIcon',
                        onClick: function () {
                            var dlg = self._createDialog();
                            if (self.labels) {
                                arrayUtil.forEach(self.labels, function(item){
                                    item.id = Math.random();
                                });
                                self._setGrid(self.labels);
                                self.tempLabels = lang.clone(self.labels);
                               // self._setLanguageComboBox(self.labels);
                            }
                            dlg.show();
                            self.labelGrid.resize();
                            self.labelGrid.refresh();
                        }
                    }, this.labelButton);

                    this.prefLabelList = new ConceptDetailList({ }, this.prefLabelListNode);
                    this.altLabelList = new ConceptDetailList({}, this.altLabelListNode);
                    this.hiddenLabelList = new ConceptDetailList({}, this.hiddenLabelListNode);


                },

                _createDialog: function () {
                    var self = this;
                    var dlg = new Dialog({
                        style: "width: 600px",
                        title: "Add Labels",
                        doLayout: true
                    });

                    var mainDiv = domConstruct.create("div");
                    domConstruct.place(mainDiv, dlg.containerNode);
                    var tableBoxDiv = domConstruct.create("div");
                    domConstruct.place(tableBoxDiv, mainDiv, "first");
                    var labelTabForBoxes = new TableContainer({cols: 4, spacing: 10, orientation: "vert"}, tableBoxDiv);


                    this.labelType = new Memory({data: this._getLabelType(), idProperty: 'value'});

                    var labelTypeComboBox = new Select(
                        {
                            id: "TypeComboBox",
                            name: "labelTypeComboBox",
                            title: "Type of label:",
                            placeHolder: 'Select a type',
                            store: this.labelType,
                            style: { width: '120px' },
                            labelAttr: "label"

                        });

                    var langStoreComboBox = new Select({
                        id: "langStoreComboBox",
                        name: "langStoreComboBox",
                        title: "Language:",
                        store: this.languageStore,
                        style: { width: '80px' },
                        labelAttr: "name"
                    });

                    var addLabelButtonToTable = new Button
                    (
                        {
                            iconClass: 'plusIcon',
                            showLabel: false,
                            onClick: lang.hitch(this, function () {
                                self.labelGrid.store.add({
                                    id: Math.random(),
                                    label: self.titleLabel.get('value'),
                                    language: self.languageComboBox.get('displayedValue'),
                                    languageValue: self.languageComboBox.get('value'),
                                    type:self.labelTypeComboBox.get('value') ,
                                    typeDisplayed: self.labelTypeComboBox.get('displayedValue')});
                                self.labelGrid.resize();
                                self.labelGrid.refresh();

                                //self._checkPrefLabelRules(self.labelTypeComboBox.get('value'));

                            })
                        }
                    );

                    var titleLabel = new TextBox({id: "titleLabel", title: "Title:"});

                    self.titleLabel = titleLabel;
                    self.labelTypeComboBox = labelTypeComboBox;
                    self.languageComboBox = langStoreComboBox;

                    labelTabForBoxes.addChild(titleLabel);
                    labelTabForBoxes.addChild(langStoreComboBox);
                    labelTabForBoxes.addChild(labelTypeComboBox);
                    labelTabForBoxes.addChild(addLabelButtonToTable);
                    labelTabForBoxes.startup();

                    var gridDiv = domConstruct.create("div");
                    var labelGrid = this._createGrid(gridDiv);
                    domConstruct.place(gridDiv, mainDiv, "last");

                    self.labelGrid = labelGrid;

                    var actionBar = domConstruct.create("div", {
                        'class': "dijitDialogPaneActionBar"
                    }, dlg.containerNode);

                    var addBtn = new Button({
                        "label": "Save"
                    }).placeAt(actionBar);
                    var cancelBtn = new Button({
                        "label": "Cancel"
                    }).placeAt(actionBar);

                    addBtn.onClick = function () {

                        self._createNodeList(self.labelGrid.store.data);
                        self.labels = self.labelGrid.store.data;
                        self.SetEditLabelButton();
                        dlg.hide();
                    };
                    cancelBtn.onClick = function () {
                        self.labels = lang.clone(self.tempLabels);
                        dlg.hide();
                    };

                    on(self.labelTypeComboBox, "change", function () {

                         //   self._checkPrefLabelRules(self.labelTypeComboBox.get('value'));

                        }
                    );

                    on(dlg, "hide", function () {
                        titleLabel.destroy();
                        labelTypeComboBox.destroy();
                        langStoreComboBox.destroy();
                    });

                    return dlg;


                },

                _getLabelType: function () {

                    var Type = [
                        {label: "Preferred", value: "prefLabel"},
                        {label: "Alternative", value: "altLabel"},
                        {label: "Hidden", value: "hiddenLabel"}
                    ];

                    return Type;
                },

                _createGrid: function (gridDiv) {
                    var self = this;

                    var gridStore = new Memory({
                        data: []
                    });

                    var columns = {
                        label: editor({
                            label: "Title",
                            field: "label",
                            autoSave: true,
                            editorArgs: {maxHeight: 150}
                        }, TextBox),
                        languageValue: editor({
                            label: "language",
                            field: "languageValue",
                            autoSave: true,
                            editorArgs: {store: self.languageStore , maxHeight: 150, style: "width:80px;", labelAttr: "name"}
                        }, Select),
                        type: editor({
                            label: "Type",
                            field: "type",
                            autoSave: true,
                            editorArgs: {store: self.labelType , maxHeight: 150, style: "width:80px;", labelAttr: "label"}
                        }, Select),
                        remove: {
                            label: "",
                            resizable: false,
                            renderCell: function (object, value, node, options) {
                                if (!object) return null;
                                var div = domConstruct.create("div", {'innerHTML': '' });
                                var a = domConstruct.create("a", {
                                    href: "#",
                                    title: "Verwijder deze note",
                                    innerHTML: 'remove',
                                    onclick: function (evt) {
                                        evt.preventDefault();
                                        grid.get('store').data = arrayUtil.filter(grid.get('store').data, function (item) {
                                            return !(object.label == item.label
                                            && object.language == item.language
                                            && object.type == item.type)
                                        });
                                        grid.refresh();
                                    }
                                }, div);
                                return div;
                            }
                        }
                    };

                    var grid = new (declare([OnDemandGrid, ColumnHider]))({
                        columns: columns,
                        store: gridStore
                    }, gridDiv);

                    grid.startup();

                    return grid;
                },
                _createNodeList: function (labels) {
                    var mapLabel = this.prefLabelList.mapLabelsForList(labels, "prefLabel");
                    this.prefLabelList.buildList(mapLabel, "Preferred labels", false);
                    mapLabel = this.altLabelList.mapLabelsForList(labels, "altLabel");
                    this.altLabelList.buildList(mapLabel, "Alternate labels", false);
                    mapLabel = this.hiddenLabelList.mapLabelsForList(labels, "hiddenLabel");
                    this.hiddenLabelList.buildList(mapLabel, "Hidden labels", false);
                },
                _setGrid: function (labels) {
                    var gridStore = new Memory({
                        data: labels

                    });
                    this.labelGrid.set("store", gridStore);
                },
                _mapLabelToDisplayedLabel: function (labels, typevalue, typeToBeDisplayed) {

                    var self = this;
                    var filteredItems = arrayUtil.filter(labels, function (item) {
                        return item.type == typevalue;
                    });
                    return arrayUtil.map(filteredItems, function (item) {
                        return {label: item.label, language: item.language, languageValue: item.language, type: item.type, typeDisplayed: typeToBeDisplayed};
                    });
                },

                //not in use for the moment
                _checkPrefLabelRules: function (value) {
                    var self = this;
                    if (value == "prefLabel") {
                        var filteredPrefLabel = arrayUtil.filter(self.labelGrid.store.data, function (item) {

                                return item.typeValue == "prefLabel";

                            }
                        );
                        if (filteredPrefLabel.length > 0) {
                            arrayUtil.forEach(filteredPrefLabel, function (item) {
                                    self.languageComboBox.getOptions(item.languageValue).disabled = true;
                                    self.languageComboBox.getOptions(item.languageValue).selected = false;
                                }
                            );
                            var enabledLanguages=arrayUtil.filter(self.languageComboBox.get("options"),function(item)
                            {
                                return item.disabled==false;
                            });
                            if (enabledLanguages.length > 0) {
                                if (self.labelTypeComboBox.get("value") == "prefLabel") {
                                    self.languageComboBox.getOptions(enabledLanguages[0].value).selected = true;
                                    self.languageComboBox.set("displayedValue", enabledLanguages[0].label);
                                }
                                if (enabledLanguages.length == 1) {
                                    arrayUtil.forEach(self.labelTypeComboBox.get("options"), function (item) {
                                            self.labelTypeComboBox.getOptions(item.value).disabled = false;
                                        }
                                    );
                                }
                            }
                            else {
                                self.labelTypeComboBox.getOptions("altLabel").selected = true;
                                self.labelTypeComboBox.getOptions("prefLabel").selected = false;
                                self.labelTypeComboBox.getOptions("prefLabel").disabled = true;
                                self.labelTypeComboBox.set("displayedValue", self.labelTypeComboBox.getOptions("altLabel").label);
                                arrayUtil.forEach(self.languageComboBox.get("options"), function (item) {
                                        self.languageComboBox.getOptions(item.value).disabled = false;
                                    }
                                );
                                self.languageComboBox.reset();
                            }
                        }
                        else {
                            self._resetLanguageComboBox();
                        }
                    }
                    else {
                        self._resetLanguageComboBox();
                    }
                },

                _resetLanguageComboBox: function () {
                    var self=this;
                    arrayUtil.forEach(self.languageComboBox.get("options"), function (item) {
                            self.languageComboBox.getOptions(item.value).disabled = false;
                        }
                    );

                },
                getLabels: function () {
                    if(this.labelGrid)
                    {
                     return  arrayUtil.map(this.labelGrid.store.data, function (label) {
                        return {"type": label.type, "language": label.languageValue, "label": label.label};
                        });
                    }
                    else
                    {
                        return  arrayUtil.map(this.labels, function (label) {
                        return {"type": label.type, "language": label.languageValue, "label": label.label};
                        });

                    }

                },

                setLabels: function (labels) {
                    this.labels = this._mapLabelToDisplayedLabel(labels, "prefLabel", "Preferred");
                    this.labels.push.apply(this.labels, this._mapLabelToDisplayedLabel(labels, "altLabel", "Alternative"));
                    this.labels.push.apply(this.labels, this._mapLabelToDisplayedLabel(labels, "hiddenLabel", "Hidden"));
                    this._createNodeList(this.labels);
                    this.tempLabels = lang.clone(this.labels);
                },

                SetEditLabelButton: function () {
                    this.EditLabelButton.set("label", "Edit labels");
                    this.EditLabelButton.set("iconClass", "");

                },
                reset: function () {
                    this.prefLabelList.reset();
                    this.altLabelList.reset();
                    this.hiddenLabelList.reset();
                    this.labels = null;
                    this.tempLabels = null;
                    this.labelGrid=null;
                    this.EditLabelButton.set("label", "Add labels");
                    this.EditLabelButton.set("iconClass", "plusIcon");
                }
            });
    });
