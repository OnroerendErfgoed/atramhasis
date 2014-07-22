define([
        "dojo/_base/declare",
        "dijit/Dialog",
        "dijit/_WidgetBase",
        "dijit/_TemplatedMixin",
        "dijit/form/Form",
        "dijit/form/Button",
        "dijit/form/Select",
        "dgrid/OnDemandGrid",
        "dijit/form/TextBox",
        "dojox/layout/TableContainer",
        "dojo/_base/lang",
        "dojo/dom-construct",
        "dojo/store/Memory",
        "dojo/store/Observable",
        "dgrid/editor",
        "dojo/query",
        "dgrid/extensions/ColumnHider",
        "dojo/_base/array",
        "dojo/on",
        "dojo/text!./templates/LabelManager.html"

    ],
    function (declare, Dialog, WidgetBase, TemplatedMixin, Form, Button, Select, OnDemandGrid, TextBox, TableContainer, lang, domConstruct, Memory, Observable, editor, query, ColumnHider, arrayUtil,on, template) {
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
                prefLanguage:null,
                labels: null,

                buildRendering: function () {
                    this.inherited(arguments);
                },
                postCreate: function () {
                    this.inherited(arguments);
                    var self = this;
                    //noinspection CommaExpressionJS

                    this.LabelLabel.innerHTML = this.title;

                    new Button({
                        label: "Add Labels",
                        showLabel: false,
                        iconClass: 'plusIcon',
                        onClick: function () {
                            var dlg = self._createDialog();
                            if (self.labels) {
                                self._setGrid(self.labels);
                            }
                            dlg.show();
                            self.labelGrid.resize();
                            self.labelGrid.refresh();
                        }
                    }, this.labelButton)


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


                    var labelType = this._getLabelType();

                    var labelTypeComboBox = new Select(
                        {
                            id: "TypeComboBox",
                            name: "labelTypeComboBox",
                            title: "Type of label:",
                            placeHolder: 'Select a type',
                            options: labelType,
                            style: { width: '120px' }

                        });
                    var languages = this._getLanguages();
                    self.prefLanguage=languages;
                    var langStoreComboBox = new Select
                    (
                        {
                            id: "langStoreComboBox",
                            name: "langStoreComboBox",
                            title: "Language:",
                            placeHolder: 'Select a language',
                            options: languages,
                            style: { width: '80px' }

                        }
                    );

                    var addLabelButtonToTable = new Button
                    (
                        {
                            iconClass: 'plusIcon',
                            showLabel: false,
                            onClick: lang.hitch(this, function () {

                                console.log("Add label to tabel in add label dialog");

                                self.labelGrid.store.add({
                                    label: self.titleLabel.get('value'),
                                    language: self.languageComboBox.get('displayedValue'),
                                    languageValue: self.languageComboBox.get('value'),
                                    type: self.labelTypeComboBox.get('displayedValue'),
                                    typeValue: self.labelTypeComboBox.get('value')});
                                self.labelGrid.resize();
                                self.labelGrid.refresh();

                                if(self.labelTypeComboBox.get('value')=="prefLabel")
                                {

                                        self.languageComboBox.removeOption(self.languageComboBox.get('value'));
                                        self.prefLanguage=self.languageComboBox.get("options");
                                }

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
                        class: "dijitDialogPaneActionBar"
                    }, dlg.containerNode);

                    var addBtn = new Button({
                        "label": "Add"
                    }).placeAt(actionBar);
                    var cancelBtn = new Button({
                        "label": "Cancel"
                    }).placeAt(actionBar);

                    addBtn.onClick = function () {

                        self._createNodeList(self.labelGrid.store.data);
                         self.labels=self.labelGrid.store.data;
                        dlg.hide();
                    };
                    cancelBtn.onClick = function () {
                        dlg.hide();
                    };

                    on(self.labelTypeComboBox,"change",function()
                        {
                             if(self.labelTypeComboBox.get('value')=="prefLabel")
                            {

                                 self.languageComboBox.set("Options",self.prefLanguage);
                                self.languageComboBox.reset();
                            }
                            else
                            {
                                 self.languageComboBox.set("Options",self._getLanguages());
                                self.languageComboBox.reset();

                            }
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

                _getLanguages: function () {
                    var languages = [
                        {label: "NL", value: "nl"},
                        {label: "Fr", value: "fr"},
                        {label: "En", value: "en"}

                    ];

                    return languages;

                },
                _createGrid: function (gridDiv) {
                    var columns;
                    columns = [
                        {label: "Title", field: "label"},
                        {label: "Language", field: "language"},
                        {label: "Language", field: "languageValue", unhidable: true, hidden: true},
                        {label: "Type", field: "type"},
                        {label: "Type", field: "typeValue", unhidable: true, hidden: true},
                        editor({label: " ", field: 'button',
                                editorArgs: {label: "delete",showLabel :false, iconClass: 'minIcon', onClick: function (event) {

                                    var row = grid.row(event);
                                    var itemToDelete = row.data.id;
                                    grid.store.remove(itemToDelete);
                                    grid.resize();
                                    grid.refresh();
                                }
                                }},
                            Button)
                    ];
                    var gridStore = new Memory({
                        data: []

                    });

                    var observableStore = new Observable(gridStore);

                    var grid = new (declare([OnDemandGrid, ColumnHider]))({
                        columns: columns,
                        store: observableStore,
                        selectionMode: "single" // for Selection; only select a single row at a time
                    }, gridDiv);

                    grid.startup();

                    return grid;
                },


                _createNodeList: function (labels) {
                    var labelListNode = this.labelListNode;
                    query("li", labelListNode).forEach(domConstruct.destroy);
                    arrayUtil.forEach(labels, function (label) {
                        domConstruct.create("li", {
                            innerHTML: "<b>" + label.label + "</b> (<em>" + label.language + "</em>): " + label.type
                        }, labelListNode);
                    });
                },

                _setGrid: function (labels) {
                    var gridStore = new Memory({
                        data: labels

                    });
                    this.labelGrid.set("store", gridStore);


                },


                getLabels: function () {
                    return  arrayUtil.map(this.labelGrid.store.data, function (label) {
                        return {"type": label.typeValue, "language": label.languageValue, "label": label.label};
                    });
                },

                setLabels: function (labels) {
                    //todo: implement this
                    console.log("set labels: " + labels);
                    this._createNodeList(labels);
                    this.labels=labels;
                },

                reset: function () {
                    var labelListNode = this.labelListNode;
                    query("li", labelListNode).forEach(domConstruct.destroy);
                    this.labels=null;
                }
            });
    });
