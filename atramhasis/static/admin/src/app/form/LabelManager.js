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
        "dojo/text!./templates/LabelManager.html"

    ],
    function (declare, Dialog, WidgetBase, TemplatedMixin, Form, Button, Select, OnDemandGrid, TextBox, TableContainer, lang, domConstruct, Memory, Observable, editor, query, ColumnHider, arrayUtil, template) {
        return declare(
            "app/form/LabelManager",
            [WidgetBase, TemplatedMixin],
            {
                templateString: template,

                name: 'LabelManager',
                grid: null,
                titleLabel: null,
                LabelGridContent: null,
                languageComboBox: null,
                labelTypeComboBox: null,

                buildRendering: function () {
                    this.inherited(arguments);
                },
                postCreate: function () {
                    this.inherited(arguments);

                    var form = new Form();
                    var self = this;
                    //noinspection CommaExpressionJS
                    form.onSubmit = function (evt) {

                        evt.preventDefault();
                        this.LabelGridContent = self.grid.store.data;
                        self._createLabelList(self.grid.store.data);
                        labelGridDialog.hide();
                    };

                    self._createEditLabelForm(form);

                    new Button({
                        label: "submit",
                        type: 'submit'
                    }).placeAt(form.containerNode);

                    var labelGridDialog = new Dialog({
                        content: form,
                        title: "Label Manager"


                    });


                    form.startup();

                    new Button({
                        label: "Manage labels",
                        onClick: function () {
                            console.log("click in labelMananger");
                            labelGridDialog.show();
                        }
                    }, this.labelButton);
                },

                _createEditLabelForm: function (form) {


                    var mainDiv = domConstruct.create("div");

                    domConstruct.place(mainDiv, form.containerNode);

                    var gridDiv = domConstruct.create("div");

                    domConstruct.place(gridDiv, mainDiv, "last");

                    var tableBoxDiv = domConstruct.create("div");
                    domConstruct.place(tableBoxDiv, mainDiv, "first");


                    var columns;
                    columns = [
                        {label: "Title", field: "label"},
                        {label: "Language", field: "language"},
                        {label: "Language", field: "languageValue", unhidable: true, hidden: true},
                        {label: "Type", field: "type"},
                        {label: "Type", field: "typeValue", unhidable: true, hidden: true},
                        editor({label: " ", field: 'button',
                                editorArgs: {label: "delete", onClick: function (event) {

                                    var row = grid.row(event);
                                    var itemToDelete = row.data.id;
                                    grid.store.remove(itemToDelete);
                                    grid.resize();
                                }
                                }},
                            Button)
                    ];
                    var gridStore = new Memory({
                        data: []

                    });

                    var observableStore = new Observable(gridStore);

                    this.grid = new (declare([OnDemandGrid, ColumnHider]))({
                        columns: columns,
                        store: observableStore,
                        selectionMode: "single" // for Selection; only select a single row at a time
                    }, gridDiv);

                    var grid = this.grid;
                    this.grid.startup();


                    var labelTabForBoxes = new TableContainer({cols: 4, spacing: 10, orientation: "vert"}, tableBoxDiv);
                    var titleLabel = new TextBox({id: "titleLabel", title: "Title:"});
                    self.titleLabel=titleLabel;
                    var labelTypeComboBox = new Select(
                        {
                            id: "labelTypeComboBox",
                            name: "labelTypeComboBox",
                            title: "Type of label:",
                            placeHolder: 'Select a type',
                            options: [
                                {label: "Preferred", value: "prefLabel"},
                                {label: "Alternative", value: "altLabel"},
                                {label: "Hidden", value: "hiddenLabel"}
                            ]
                        });
                    self.labelTypeComboBox=labelTypeComboBox;
                    var langStoreComboBox = new Select
                    (
                        {
                            id: "langStoreComboBox",
                            name: "langStoreComboBox",
                            title: "Language:",
                            placeHolder: 'Select a language',
                            options: [
                                {label: "NL", value: "nl"},
                                {label: "Fr", value: "fr"},
                                {label: "En", value: "en"}

                            ],
                            style: { width: '80px' }

                        }
                    );
                    self.languageComboBox=langStoreComboBox;
                    var addLabelButtonToTable = new Button
                    (
                        {
                            iconClass: 'plusIcon',
                            showLabel: false,
                            onClick: lang.hitch(this, function () {

                                console.log("Add label to tabel in add label dialog");

                                grid.store.add({
                                    label: titleLabel.get('value'),
                                    language: langStoreComboBox.get('displayedValue'),
                                    languageValue: langStoreComboBox.get('value'),
                                    type: labelTypeComboBox.get('displayedValue'),
                                    typeValue: labelTypeComboBox.get('value')});
                                grid.resize();
                            })
                        }
                    );
                    labelTabForBoxes.addChild(titleLabel);
                    labelTabForBoxes.addChild(langStoreComboBox);
                    labelTabForBoxes.addChild(labelTypeComboBox);
                    labelTabForBoxes.addChild(addLabelButtonToTable);
                    labelTabForBoxes.startup();
                    this.grid.resize();
                },
                _createLabelList: function (labels) {
                    var labelListNode = this.labelListNode;
                    query("li", labelListNode).forEach(domConstruct.destroy);
                    arrayUtil.forEach(labels, function (label) {
                        domConstruct.create("li", {
                            innerHTML: "<b>" + label.name + "</b> (<em>" + label.language + "</em>): " + label.type
                        }, labelListNode);
                    });
                },
                getLabels: function () {
                    var labels = this.grid.store.data;
                    var labelsToSend = [];
                    arrayUtil.forEach(labels, function (label) {

                        var labelToSend = {
                            "type": label.typeValue,
                            "language": label.languageValue,
                            "label": label.label
                        };
                        labelsToSend.push(labelToSend);
                    });
                    return labelsToSend;
                },
                reset: function () {
                    var gridStore = new Memory({
                        data: []

                    });
                    self.titleLabel.set("value", "");
                    self.languageComboBox.reset();
                    self.labelTypeComboBox.reset();
                    var observableStore = new Observable(gridStore);
                    this.grid.set("store", observableStore);
                    var labelListNode = this.labelListNode;
                    query("li", labelListNode).forEach(domConstruct.destroy);
                }
            });
    });
