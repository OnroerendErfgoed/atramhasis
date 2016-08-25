define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/dom-style',
  'dojo/json',
  'dojo/on',
  'dojo/topic',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/NoteManager.html',
  'dstore/Memory',
  'dstore/Trackable',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  '../../utils/DomUtils',
  '../dialogs/NotesDialog'
], function (
  declare,
  array,
  lang,
  domConstruct,
  domClass,
  domStyle,
  JSON,
  on,
  topic,
  _WidgetBase,
  _TemplatedMixin,
  template,
  Memory,
  Trackable,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  DomUtils,
  NotesDialog
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'note-manager',
    languageController: null,
    listController: null,
    concept: null,
    languageList: null,
    _noteStore: null,
    _noteGrid: null,
    _index: 0,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('NoteManager::postCreate');

      this.trackableMemory = declare([Memory, Trackable]);
      this._noteStore = new this.trackableMemory({ data: [] });
      if (this.concept) {
        array.forEach(this.concept.notes, lang.hitch(this, function (item) {
          item.id = this._index++;
          this._noteStore.put(item);
        }));
      }
      this._createGrid({
        collection: this._noteStore
      }, this.noteGridNode);

      this._notesDialog = new NotesDialog({
        parentNode: this,
        langList: this.languageList,
        typeList: this.listController.getNoteTypes()
      });
      on(this._notesDialog, 'add.note', lang.hitch(this, function(evt) {
        this._doAddNote(evt);
      }));
      on(this._notesDialog, 'edit.note', lang.hitch(this, function(evt) {
        this._doEditNote(evt);
      }));
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('NoteManager::startup');
      this._notesDialog.startup();
      this._noteGrid.startup();
      this._noteGrid.resize();
    },

    reset: function() {
      if (this._notesDialog) { this._notesDialog.reset(); }
      var TrackableMemory = declare([Memory, Trackable]);
      this._noteStore = new TrackableMemory({ data: [] });
      this._noteGrid.set('collection', this._noteStore);
    },

    _createGrid: function(options, node) {
      var columns = {
        note: {
          label: "Note",
          field: "note",
          renderCell: function(object) {
            if (object) {
              var div = domConstruct.create('div', {innerHTML: object.note});
              return div;
            }
          }
        },
        language: {
          label: "Language",
          field: "language",
          formatter: lang.hitch(this, function (value) {
            var lang = array.filter(this.languageList, function (obj) {
              return obj.id === value;
            })[0];
            if (lang) {
              return lang.name;
            } else {
              return '-';
            }
          })
        },
        type: {
          label: "Type",
          field: "type",
          formatter: lang.hitch(this, function (value) {
            var lang = array.filter(this.listController.getNoteTypes(), function (obj) {
              return obj.value === value;
            })[0];
            return lang.label;
          })
        },
        actions: {
          label: '',
          renderCell: lang.hitch(this, function (object) {
            if (object.id === undefined) {
              return null;
            }
            var div = domConstruct.create('div', {'class': 'dGridHyperlink'});
            domConstruct.create('a', {
              href: '#',
              title: 'Edit note',
              className: 'fa fa-pencil',
              innerHTML: '',
              style: 'margin-right: 12px;',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                this._editNote(object);
              })
            }, div);
            domConstruct.create('a', {
              href: '#',
              title: 'Remove note',
              className: 'fa fa-trash',
              innerHTML: '',
              onclick: lang.hitch(this, function (evt) {
                evt.preventDefault();
                this._removeRow(object.id);
              })
            }, div);
            return div;
          })
        }
      };

      var grid = new (declare([OnDemandGrid, DijitRegistry, ColumnResizer]))({
        collection: options.collection,
        columns: columns,
        showHeader: false,
        noDataMessage: 'No notes found',
        loadingMessage: 'Fetching data..'
      }, node);

      this._noteGrid = grid;

      grid.on('dgrid-error', function(event) {
        console.log(event.error.message);
      });
    },

    getData: function() {
      var notes = {
        notes: this._noteStore.data
      }
      return notes;
    },

    setConcept: function(concept) {
      if (concept) {
        this.concept = concept;
        this._noteStore = new this.trackableMemory({ data: [] });
        array.forEach(this.concept.notes, lang.hitch(this, function (item) {
          item.id = this._index++;
          this._noteStore.put(item);
        }));
        this._noteGrid.set('collection', this._noteStore);
      }
    },

    updateLanguages: function(languages) {
      if (languages) {
        this.languageList = languages;
        this._notesDialog.updateLanguages(languages);
      }
    },

    _addNote: function(evt) {
      evt ? evt.preventDefault(): null;
      this._notesDialog.show();
    },

    _editNote: function(note) {
      this._notesDialog.show(note);
    },

    _doAddNote: function(note) {
      var newNote = {
        language: note.lang,
        type: note.noteType,
        note: note.note
      };
      console.log(newNote);
      this._noteStore.add(newNote);
    },

    _doEditNote: function(note) {
      var editNote = {
        language: note.lang,
        type: note.noteType,
        note: note.note,
        id: note.id
      };
      console.log(editNote);
      this._noteStore.put(editNote);
    },

    _removeRow: function(rowId) {
      this._noteStore.remove(rowId);
    }
  });
});