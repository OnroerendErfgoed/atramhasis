define([
    'dijit/_WidgetsInTemplateMixin',
    'dijit/_TemplatedMixin',
    'dijit/_WidgetBase',
    'dojo/_base/declare',
    "dijit/form/Button",
    "dijit/Dialog",
    'dijit/form/TextBox',
    "dojo/dom-construct",
    "dijit/form/Textarea",
    "dijit/form/Select",
    "dojox/layout/TableContainer",
    "dgrid/OnDemandGrid",
    'dgrid/Keyboard',
    'dgrid/Selection',
    'dgrid/extensions/DijitRegistry',
    "dgrid/editor",
    "dgrid/extensions/ColumnHider",
    "dojo/_base/lang",
    "dojo/store/Memory",
    'dojo/store/Cache',
    'dojo/store/Observable',
    "dojo/on",
    "dojo/store/JsonRest",
    "dojo/_base/array",
    "./ConceptDetailList",
    'dojo/text!./templates/NoteManager.html'
], function (
    WidgetsInTemplateMixin,
    TemplatedMixin,
    WidgetBase,
    declare,
    Button,
    Dialog,
    TextBox,
    domConstruct,
    Textarea,
    Select,
    TableContainer,
    OnDemandGrid,
    Keyboard,
    Selection,
    DijitRegistry,
    editor,
    ColumnHider,
    lang,
    Memory,
    Cache,
    Observable,
    on,
    JsonRest,
    arrayUtil,
    ConceptDetailList,
    template) {
    return declare("app/form/NoteManager", [WidgetBase, TemplatedMixin, WidgetsInTemplateMixin], {
        templateString: template,
        name: 'NoteManager',
        title: 'Notes:',
        noteArea: null,
        labelComboBox: null,
        languageComboBox: null,
        noteGrid: null,
        notes: null,
        tempNotes: null,
        editNoteButton:null,

        postMixInProperties: function () {
            this.inherited(arguments);
        },

        buildRendering: function () {
            this.inherited(arguments);
        },

        postCreate: function (notes) {
            var self = this;
            self.inherited(arguments);

            self.changeNoteList = new ConceptDetailList({ }, self.changeNoteListNode);
            self.definitionList = new ConceptDetailList({}, self.definitionListNode);
            self.editorialNoteList = new ConceptDetailList({}, self.editorialNoteListNode);
            self.exampleList = new ConceptDetailList({ }, self.exampleListNode);
            self.historyNoteList = new ConceptDetailList({}, self.historyNoteListNode);
            self.scopeNoteList = new ConceptDetailList({}, self.scopeNoteListNode);
            self.noteList = new ConceptDetailList({}, self.noteListNode);

            self.editNoteButton= new Button({
                label: "Add Notes",
                showLabel: true,
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
                style: "width: 800px",
                title: "Save Notes",
                doLayout: true
            });
            var mainDiv = domConstruct.create("div");
            domConstruct.place(mainDiv, dlg.containerNode);
            var tableBoxDiv = domConstruct.create("div");
            domConstruct.place(tableBoxDiv, mainDiv, "first");
            var labelTabForBoxes = new TableContainer({cols: 3, spacing: 10, orientation: "vert"}, tableBoxDiv);
            this.noctypes = Observable( Cache( JsonRest({
                target: "/notetypes",
                idProperty: 'key'
            }), Memory()));
            var labelComboBox = new Select(
                {
                    id: "labelComboBox",
                    name: "labelTypeComboBox",
                    title: "Type of note:",
                    placeHolder: 'Select a type',
                    store: this.noctypes,
                    style: { width: '130px' },
                    labelAttr: "label"
                });
            //labelComboBox.set("value", 'Select a type');

            var languageComboBox = new Select({
                id: "languageComboBox",
                name: "languageComboBox",
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

                        console.log("Add note to note tabel in note dialog dialog");

                        noteGrid.store.add({
                            label: self.noteArea.get('value'),
                            language: self.languageComboBox.get('displayedValue'),
                            languageValue: self.languageComboBox.get('value'),
                            type:  self.labelComboBox.get('value'),
                            typeDisplayed: self.labelComboBox.get('displayedValue')});
                        noteGrid.resize();
                        self.noteGrid.refresh();
                    })
                }
            );

            var noteArea = new Textarea({
                name: "noteArea",
                title: "Note:",
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
                'class': "dijitDialogPaneActionBar"
            }, dlg.containerNode);

            var addBtn = new Button({
                "label": "Save"
            }).placeAt(actionBar);
            var cancelBtn = new Button({
                "label": "Cancel"
            }).placeAt(actionBar);

            addBtn.onClick = function () {

                self._createNodeList(self.noteGrid.store.data);
                self.notes=self.noteGrid.store.data;
                self.setEditNoteButton();
                dlg.hide();
            };
            cancelBtn.onClick = function () {
                self.notes = lang.clone(self.tempNotes);
                self._setGrid(self.notes);
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
                {label: "Type", field: "typeDisplayed"},
                {label: "Type", field: "type", unhidable: true, hidden: true},
                {
                    label: ' ',
                    field: 'complexCell',
                    renderCell: function (object, value, node, options) {
                        return new Button({
                            label: "remove",
                            onClick: function () {
                                //re-add fitlered data, removing items directly is not possible without id's
                                grid.get('store').data = arrayUtil.filter(grid.get('store').data, function (item) {
                                    return !(object.label == item.label
                                    && object.language == item.language
                                    && object.type == item.type)
                                });
                                grid.refresh();
                            }
                        }).domNode;
                    }
                }
            ];
            var self =this;
            var columns = {
                label: editor({
                    label: "Note",
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
                    editorArgs: {store: self.noctypes , maxHeight: 150, style: "width:80px;", labelAttr: "label"}
                }, Select),
                remove: {
                    label: "",
                    resizable: false,
                    renderCell: function (object, value, node, options) {
                        return new Button({
                            label: "remove",
                            showLabel: false,
                            iconClass: "minIcon",
                            onClick: function () {
                                //re-add fitlered data, removing items directly is not possible without id's
                                grid.store.data = arrayUtil.filter(grid.store.data, function (item) {
                                    return !(object.label == item.label
                                      && object.language == item.language
                                      && object.type == item.type)
                                });
                                grid.refresh();
                            }
                        }).domNode;
                    }
                }
            };
            var gridStore = new Memory({
                data: []

            });
           var grid = new (declare([OnDemandGrid, Keyboard, Selection, DijitRegistry]))({
                columns: columns,
                store: gridStore,
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

                    };
                    itemsToDisplay.push(labelToSend);
                })

            });
            return itemsToDisplay;
        },

        _createNodeList: function (notes) {
            this.definitionList.buildList(this.definitionList.mapLabelsForList(notes, "definition"), "Definition", false);
            this.changeNoteList.buildList(this.changeNoteList.mapLabelsForList(notes, "changeNote"), "Change note", false);
            this.editorialNoteList.buildList(this.editorialNoteList.mapLabelsForList(notes, "editorialNote"), "Editorial note", false);
            this.exampleList.buildList(this.exampleList.mapLabelsForList(notes, "example"), "Example", false);
            this.historyNoteList.buildList(this.historyNoteList.mapLabelsForList(notes, "historyNote"), "Historynote", false);
            this.scopeNoteList.buildList(this.scopeNoteList.mapLabelsForList(notes, "scopeNote"), "Scopenote", false);
            this.noteList.buildList(this.noteList.mapLabelsForList(notes, "note"), "Note", false);
        },

        _mapNoteToDisplayInGrid: function (notes, typevalue, typeToBeDisplayed) {

            var self = this;
            var filteredItems = arrayUtil.filter(notes, function (item) {
                return item.type == typevalue;
            });

            return arrayUtil.map(filteredItems, function (item) {
                return {label: item.note, language: item.language, languageValue: item.language, type:item.type , typeDisplayed:typeToBeDisplayed};
            });
        },

        geNotes: function () {
            if(this.noteGrid) {
                var notes = this.noteGrid.get('store').data;
                var notesToSend = [];
                arrayUtil.forEach(notes, function (note) {
                    var noteToSend = {
                        "type": note.type,
                        "language": note.languageValue,
                        "note": note.label
                    };
                    notesToSend.push(noteToSend);
                });
                return notesToSend;
            }
            else
            {
                return  arrayUtil.map(this.notes, function (note) {
                        return {"type": note.type, "language": note.languageValue, "note": note.label};
                        });

            }
        },
        reset: function () {
            this.notes = null;
            this.tempNotes = null;
            this.changeNoteList.reset();
            this.definitionList.reset();
            this.editorialNoteList.reset();
            this.exampleList.reset();
            this.historyNoteList.reset();
            this.scopeNoteList.reset();
            this.noteList.reset();
            this.editNoteButton.set("label","Add Notes");
            this.editNoteButton.set("iconClass","plusIcon");
        },
        setNotes: function (notes) {
            this.notes = this._mapNoteToDisplayInGrid(notes, "definition", "Definition");
            this.notes.push.apply(this.notes, this._mapNoteToDisplayInGrid(notes, "changeNote", "Change note"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayInGrid(notes, "editorialNote", "Editorial note"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayInGrid(notes, "example", "Example"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayInGrid(notes, "historyNote", "Historynote"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayInGrid(notes, "scopeNote", "Scopenote"));
            this.notes.push.apply(this.notes, this._mapNoteToDisplayInGrid(notes, "note", "Note"));
            this._createNodeList(this.notes);
            this.tempNotes = lang.clone(this.notes);
        },

        setEditNoteButton:function()
        {
            this.editNoteButton.set("label","Edit Notes");
             this.editNoteButton.set("iconClass","");

        },

        _setGrid: function (notes) {
            var gridStore = new Memory({
                data: notes
            });
            this.noteGrid.set("store", gridStore);
        }
    });
});
