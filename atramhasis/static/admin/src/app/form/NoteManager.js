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
    "./ConceptDetailList",
    'dojo/text!./templates/NoteManager.html'
], function (WidgetsInTemplateMixin, TemplatedMixin, WidgetBase, declare, Button, Dialog, domConstruct, Textarea, Select, TableContainer, OnDemandGrid, ColumnHider, Observable, editor, lang, Memory, on, JsonRest, query, arrayUtil,ConceptDetailList, template) {
    return declare("app/form/NoteManager", [WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
        templateString: template,
        name: 'NoteManager',
        title: 'Notes:',
        noteArea: null,
        labelComboBox: null,
        languageComboBox: null,
        noteGrid: null,
        notes: null,
        tempNotes:null,


        postMixInProperties: function () {
            this.inherited(arguments);
        },

        buildRendering: function () {
            this.inherited(arguments);
        },

        postCreate: function (notes) {
            var self = this;
            self.inherited(arguments);

            self.changeNoteList = new ConceptDetailList ({ }, self.changeNoteListNode);
            self.definitionList = new ConceptDetailList({}, self.definitionListNode);
            self.editorialNoteList = new ConceptDetailList({}, self.editorialNoteListNode);
            self.exampleList = new ConceptDetailList ({ }, self.exampleListNode);
            self.historyNoteList = new ConceptDetailList({}, self.historyNoteListNode);
            self.scopeNoteList = new ConceptDetailList({}, self.scopeNoteListNode);
            self.noteList = new ConceptDetailList({}, self.noteListNode);


            self.noteLabel.innerHTML = this.title;

            new Button({
                label: "Add Notes",
                showLabel: false,
                iconClass: 'plusIcon',
                onClick: function () {
                    var dlg = self._createDialog();
                    if (self.notes) {
                        self._setGrid(self.notes);
                    }
                    dlg.show();
                    self.noteGrid.resize();
                    self.noteGrid.refresh();
                    self.labelComboBox.reset();
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
            labelComboBox.set("value",'Select a type');

            var languages = this._getLanguages();
            var languageComboBox = new Select
            (
                {
                    id: "languageComboBox",
                    name: "languageComboBox",
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

                        console.log("Add note to note tabel in note dialog dialog");

                        noteGrid.store.add({
                            label: self.noteArea.get('value'),
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
                self.notes = self.noteGrid.store.data;

                dlg.hide();
            };
            cancelBtn.onClick = function () {
                this.notes=lang.clone(this.tempNotes);
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
                {label: "Note", field: "label"},
                {label: "Language", field: "language"},
                {label: "Language", field: "languageValue", unhidable: true, hidden: true},
                {label: "Type", field: "type"},
                {label: "Type", field: "typeValue", unhidable: true, hidden: true},
                editor({label: " ", field: 'button',
                        editorArgs: {label: "delete", showLabel: false, iconClass: 'minIcon', onClick: function (event) {

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
        _getLanguages: function () {
            var languages = [
                {label: "NL", value: "nl"},
                {label: "FR", value: "fr"},
                {label: "EN", value: "en"}

            ];

            return languages;

        },
     /*   _createNodeList: function (notes) {
            var labelListNode = this.NoteListNode;
            query("li", labelListNode).forEach(domConstruct.destroy);
            arrayUtil.forEach(notes, function (note) {
                domConstruct.create("li", {
                    innerHTML: "<b>" + note.note + "</b> (<em>" + note.language + "</em>): " + note.type
                }, labelListNode);
            });
        },*/

        _createNodeList: function (notes)
        {
             this.definitionList.buidList(this.definitionList.mapLabelsForList(notes, "definition"), "Definition", false);
             this.changeNoteList.buidList(this.changeNoteList.mapLabelsForList(notes, "changeNote"), "Change note", false);
             this.editorialNoteList.buidList(this.editorialNoteList.mapLabelsForList(notes, "editorialNote"), "Editorial note", false);
             this.exampleList.buidList(this.exampleList.mapLabelsForList(notes, "example"), "Example", false);
             this.historyNoteList.buidList(this.historyNoteList.mapLabelsForList(notes, "historyNote"), "Historynote", false);
             this.scopeNoteList.buidList(this.scopeNoteList.mapLabelsForList(notes, "scopeNote"), "Scopenote", false);
             this.noteList.buidList(this.noteList.mapLabelsForList(notes, "note"), "Note", false);
         },

         _mapNoteToDisplayedNote: function (notes, typevalue, typeToBeDisplayed) {

                    var self=this;
                    var filteredItems = arrayUtil.filter(notes, function (item) {
                        return item.type == typevalue;
                    });

                    return arrayUtil.map(filteredItems, function (item) {
                        return {label: item.note, language:self._getLanguageToDisplay(item.language), languageValue: item.language, type: typeToBeDisplayed, typeValue: item.type};
                    });
                },
                            _getLanguageToDisplay: function (language) {
                    switch (language) {
                        case "nl":
                            return "NL";
                            break;
                        case "fr":
                            return "FR";
                            break;
                        case "en":
                            return "EN";
                            break;
                        default:
                            return language;
                            break;
                    }

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
            this.notes = null;
            this.tempNotes=null;
             this.changeNoteList.reset();
            this.definitionList.reset();
            this.editorialNoteList.reset();
            this.exampleList.reset();
            this.historyNoteList.reset();
            this.scopeNoteList.reset();
            this.noteList = new ConceptDetailList({}, self.noteListNode);
        },

        setNotes: function (notes) {

            this.notes = this._mapNoteToDisplayedNote(notes, "definition", "Definition");
            this.notes.push.apply(this.notes, this._mapNoteToDisplayedNote(notes, "changeNote", "Change note"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayedNote(notes, "editorialNote", "Editorial note"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayedNote(notes, "example", "Example"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayedNote(notes, "historyNote", "Historynote"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayedNote(notes, "scopeNote", "Scopenote"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayedNote(notes, "note", "Note"));
            this._createNodeList(this.notes);
            this._createNodeList(notes);
            this.tempNotes=lang.clone(this.notes);
        },

        _setGrid: function (notes) {
            var gridStore = new Memory({
                data: notes

            });
            this.noteGrid.set("store", gridStore);

        }
    });
});
