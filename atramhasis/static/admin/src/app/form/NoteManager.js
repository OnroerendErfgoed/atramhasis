define([
    'dijit/_WidgetsInTemplateMixin',
    'dijit/_TemplatedMixin',
    'dijit/_WidgetBase',
    'dojo/_base/declare',
    "dijit/form/Button",
    "dijit/Dialog",
    "dojo/dom-construct",
    "dijit/form/Textarea",
    "dijit/form/Select",
    "dojox/layout/TableContainer",
    "dgrid/OnDemandGrid",
    "dgrid/extensions/ColumnHider",
    "dojo/store/Observable",
    "dgrid/editor",
    "dojo/_base/lang",
    "dojo/store/Memory",
    "dojo/on",
    'dojo/text!./templates/NoteManager.html'
], function (WidgetsInTemplateMixin, TemplatedMixin, WidgetBase, declare, Button, Dialog, domConstruct, Textarea, Select, TableContainer, OnDemandGrid, ColumnHider, Observable, editor,lang,Memory,on, template) {
    return declare("app/form/NoteManager", [WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
        templateString: template,
        name: 'NoteManager',
        title: 'Notes:',
        postMixInProperties: function () {
            this.inherited(arguments);
        },

        buildRendering: function () {
            this.inherited(arguments);
        },

        postCreate: function () {
            this.inherited(arguments);
            var self = this;
            this.noteLabel.innerHTML = this.title;

            new Button({
                label: "Add Notes",
                showLabel: false,
                iconClass: 'plusIcon',
                onClick: function () {
                    var dlg = self._createDialog();
                    dlg.show();
                }
            }, this.noteButton)


        },

        startup: function () {
            this.inherited(arguments);
            var self = this;
        },

        _createDialog: function () {
            var self = this;

            var dlg = new Dialog({
                style: "width: 600px",
                title: "Add Notes",
                doLayout: true
            });
            var mainDiv = domConstruct.create("div");
            domConstruct.place(mainDiv, dlg.containerNode);
            var tableBoxDiv = domConstruct.create("div");
            domConstruct.place(tableBoxDiv, mainDiv, "first");
            var labelTabForBoxes = new TableContainer({cols: 3, spacing: 10, orientation: "vert"}, tableBoxDiv);
            var labelComboBox = new Select(
                {
                    id: "labelComboBox",
                    name: "labelTypeComboBox",
                    title: "Type of note:",
                    placeHolder: 'Select a type',
                    options: [
                        {label: "Preferred", value: "prefLabel"},
                        {label: "Alternative", value: "altLabel"},
                        {label: "Hidden", value: "hiddenLabel"}
                    ]
                });

            var languageComboBox = new Select
            (
                {
                    id: "languageComboBox",
                    name: "languageComboBox",
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

            var addLabelButtonToTable = new Button
            (
                {
                    iconClass: 'plusIcon',
                    showLabel: false,
                    onClick: lang.hitch(this, function () {

                        console.log("Add note to note tabel in note dialog dialog");
                        alert("ok");

                    })
                }
            );

                        var noteArea = new Textarea({
                name: "noteArea",
                colspan:"3"
            });
            noteArea.startup();
            labelComboBox.startup();
            languageComboBox.startup();


            labelTabForBoxes.addChild(languageComboBox);
            labelTabForBoxes.addChild(labelComboBox);
            labelTabForBoxes.addChild(addLabelButtonToTable);
            labelTabForBoxes.addChild(noteArea);
            labelTabForBoxes.startup();

            var areaDiv = domConstruct.create("div");

            domConstruct.place(areaDiv, mainDiv, "last");


            var gridDiv = domConstruct.create("div");

            var noteGrid=self._createGrid(gridDiv);


            domConstruct.place(gridDiv, mainDiv, "last");


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
                alert("ok");

                dlg.hide();
            };
            cancelBtn.onClick = function () {
                dlg.hide();
            };
             on(dlg, "hide", function(){
                  noteArea.destroy();
                 languageComboBox.destroy();
                 labelComboBox.destroy();
            });
            return dlg;

        },


        _createGrid: function (gridDiv) {
            var columns;
            columns = [
                {label: "Note", field: "note"},
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

            var grid = new (declare([OnDemandGrid, ColumnHider]))({
                columns: columns,
                store: observableStore,
                selectionMode: "single" // for Selection; only select a single row at a time
            }, gridDiv);

            grid.startup();
            return grid;
        },

        _getNoteType:function(){




        }


    });
});
