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
    "dojo/store/JsonRest",
    "dojo/query",
    "dojo/_base/array",
    'dojo/text!./templates/NoteManager.html'
], function (WidgetsInTemplateMixin, TemplatedMixin, WidgetBase, declare, Button, Dialog, domConstruct, Textarea, Select, TableContainer, OnDemandGrid, ColumnHider, Observable, editor, lang, Memory, on, JsonRest, query, arrayUtil, template) {
    return declare("app/form/NoteManager", [WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
        templateString: template,
        name: 'NoteManager',
        title: 'Notes:',
        noteArea: null,
        labelComboBox: null,
        languageComboBox: null,
        noteGrid: null,
        notes:null,
        postMixInProperties: function () {
            this.inherited(arguments);
        },

        buildRendering: function () {
            this.inherited(arguments);
        },

        postCreate: function (notes) {
            this.inherited(arguments);
            var self = this;
            this.noteLabel.innerHTML = this.title;

            new Button({
                label: "Add Notes",
                showLabel: false,
                iconClass: 'plusIcon',
                onClick: function () {
                    var dlg = self._createDialog();
                    if(self.notes)
                    {
                       self._setGrid(self.notes);
                    }
                    dlg.show();
                       self.noteGrid.resize();
                                             self.noteGrid.refresh();
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
            var notetype = self._getNoteType();
            var labelComboBox = new Select(
                {
                    id: "labelComboBox",
                    name: "labelTypeComboBox",
                    title: "Type of note:",
                    placeHolder: 'Select a type',
                    options: notetype,
                    style: { width: '130px' }
                });
            var languages=this._getLanguages();
            var languageComboBox = new Select
            (
                {
                    id: "languageComboBox",
                    name: "languageComboBox",
                    title: "Language:",
                    placeHolder: 'Select a language',
                    options:languages,
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

                        noteGrid.store.add({
                            note: self.noteArea.get('value'),
                            language: self.languageComboBox.get('displayedValue'),
                            languageValue: self.languageComboBox.get('value'),
                            type: self.labelComboBox.get('displayedValue'),
                            typeValue: self.labelComboBox.get('value')});
                        noteGrid.resize();
                        self.noteGrid.refresh();
                    })
                }
            );

            var noteArea = new Textarea({
                name: "noteArea",
                colspan: "3"
            });
            noteArea.startup();
            labelComboBox.startup();
            languageComboBox.startup();

            labelComboBox.reset();

            self.noteArea = noteArea;
            self.labelComboBox = labelComboBox;
            self.languageComboBox = languageComboBox;


            labelTabForBoxes.addChild(languageComboBox);
            labelTabForBoxes.addChild(labelComboBox);
            labelTabForBoxes.addChild(addLabelButtonToTable);
            labelTabForBoxes.addChild(noteArea);
            labelTabForBoxes.startup();

            var areaDiv = domConstruct.create("div");

            domConstruct.place(areaDiv, mainDiv, "last");


            var gridDiv = domConstruct.create("div");

            var noteGrid = self._createGrid(gridDiv);


            domConstruct.place(gridDiv, mainDiv, "last");

            self.noteGrid = noteGrid;
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

                self._createNodeList(self.noteGrid.store.data);
                self.notes=self.noteGrid.store.data;

                dlg.hide();
            };
            cancelBtn.onClick = function () {
                dlg.hide();
            };
            on(dlg, "hide", function () {
                noteArea.destroy();
                languageComboBox.destroy();
                labelComboBox.destroy();
            });
            noteGrid.resize();
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
             grid.resize();
            return grid;
        },

        _getNoteType: function () {


            var store = new JsonRest({
                target: "/notetypes",
                sortParam: "sort"
            });
            var itemsToDisplay = [];
            store.get().then(function (items) {

                arrayUtil.forEach(items, function (item) {

                    var labelToSend = {
                        "label": item.label,
                        "value": item.key

                    }
                    itemsToDisplay.push(labelToSend);
                })

            });
            return itemsToDisplay;
        },
                        _getLanguages:function()
                {
                   var languages= [
                                {label: "NL", value: "nl"},
                                {label: "Fr", value: "fr"},
                                {label: "En", value: "en"}

                            ];

                    return languages;

                },
        _createNodeList: function (notes) {
            var labelListNode = this.NoteListNode;
            query("li", labelListNode).forEach(domConstruct.destroy);
            arrayUtil.forEach(notes, function (note) {
                domConstruct.create("li", {
                    innerHTML: "<b>" + note.note + "</b> (<em>" + note.language + "</em>): " + note.type
                }, labelListNode);
            });
        },
        geNotes: function () {
            var notes = this.noteGrid.store.data;
            var notesToSend = [];
            arrayUtil.forEach(notes, function (note) {
                var noteToSend = {
                    "type": note.typeValue,
                    "language": note.languageValue,
                    "label": note.note
                };
                notesToSend.push(noteToSend);
            });
            return notesToSend;
        },
        reset: function () {
            var noteListNode = this.NoteListNode;
            query("li", noteListNode).forEach(domConstruct.destroy);
            this.notes=null;
        },

        setNotes:function(notes)
        {
            this._createNodeList(notes);
            this.notes=notes;
        },

        _setGrid:function(notes)
        {
           var gridStore = new Memory({
                data:notes

            });
              this.noteGrid.set("store",gridStore);

        }
    });
});
