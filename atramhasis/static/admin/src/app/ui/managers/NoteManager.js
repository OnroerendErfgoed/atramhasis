define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/dom-style',
  'dojo/json',
  'dojo/topic',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/NoteManager.html',
  'dstore/Memory',
  'dstore/Trackable',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  '../../utils/DomUtils'
], function (
  declare,
  array,
  lang,
  domConstruct,
  domClass,
  domStyle,
  JSON,
  topic,
  _WidgetBase,
  _TemplatedMixin,
  template,
  Memory,
  Trackable,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  DomUtils
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
      DomUtils.addOptionsToSelect(this.noteTypeSelectNode, {
        data: this.listController.getNoteTypes(),
        idProperty: 'value',
        labelProperty: 'label'
      });
      DomUtils.addOptionsToSelect(this.languageSelectNode, {
        data: this.languageList,
        idProperty: 'id',
        labelProperty: 'name'
      });
      var TrackableMemory = declare([Memory, Trackable]);
      this._noteStore = new TrackableMemory({ data: [] });
      array.forEach(this.concept.notes, lang.hitch(this, function(item){
        item.id = this._index++;
        this._noteStore.put(item);
      }));
      this._createGrid({
        collection: this._noteStore
      }, this.noteGridNode);
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('NoteManager::startup');
      this._noteGrid.startup();
    },

    _createGrid: function(options, node) {
      var columns = {
        note: {
          label: "Note",
          field: "note"
        },
        language: {
          label: "Language",
          field: "language",
          formatter: lang.hitch(this, function (value, object) {
            var lang = array.filter(this.languageList, function (obj) {
              console.log(obj, value);
              return obj.id === value;
            })[0];
            return lang.name;
          })
        },
        type: {
          label: "Type",
          field: "type",
          formatter: lang.hitch(this, function (value, object) {
            var lang = array.filter(this.listController.getNoteTypes(), function (obj) {
              console.log(obj, value);
              return obj.value === value;
            })[0];
            return lang.label;
          })
        },
        remove_label: {
          label: 'Remove',
          renderCell: lang.hitch(this, function (object) {
            if (object.id === undefined) {
              return null;
            }
            var div = domConstruct.create('div', {'class': 'dGridHyperlink'});
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
      return this._noteStore.data;
    },

    _addNote: function(evt) {
      evt ? evt.preventDefault() : null;

      var note = {
        id: this._index++,
        language: DomUtils.getSelectedOption(this.languageSelectNode),
        type: DomUtils.getSelectedOption(this.noteTypeSelectNode),
        note: this.noteTitleNode.value
      };

      if (this._validate(note)) {
        this._addRow(note);
      } else {
        topic.publish('dGrowl', 'Please fill in the fields for a new note', {'title': "Error", 'sticky': true, 'channel':'error'});
      }
    },

    _removeRow: function(rowId) {
      this._noteStore.remove(rowId);
    },

    _addRow: function(row) {
      console.log('ADD ROW', row);
      this._noteStore.add(row);
    },

    _validate: function(note) {
      var valid = true;

      if (!note.language || note.language === '') {
        valid = false;
      }
      if (!note.type || note.type === '') {
        valid = false;
      }
      if (!note.note || note.note === '') {
        valid = false;
      }

      return valid;
    }

  });
});