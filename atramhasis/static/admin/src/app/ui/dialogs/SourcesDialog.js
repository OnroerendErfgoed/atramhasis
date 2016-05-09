define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/topic',
  'dojo/text!./templates/SourcesDialog.html',
  '../../utils/HtmlEditor',
  '../../utils/DomUtils'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  topic,
  template,
  HtmlEditor,
  DomUtils
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'sources-dialog',
    title: 'Add source',
    source: null,
    _editor: null,
    edit: false,

    postCreate: function () {
      this.inherited(arguments);
      this._editor = new HtmlEditor({}, this.htmlEditorNode);
    },

    startup: function () {
      this.inherited(arguments);
      this._editor.startup();
      this._editor.addButtons(['emphasis', 'strong', 'link']);
      this._editor.setContent('');
    },

    setData: function(source) {
      this._editor.setContent(source.citation);
    },

    hide: function () {
      this.inherited(arguments);
      this.reset();
    },

    show: function (source) {
      this.inherited(arguments);
      this.reset();
      if (source) {
        this.setData(source);
        this.set('title', 'Edit source');
        this.okButtonNode.innerHTML = 'Edit';
        this.edit = true;
        this.source = source;
      } else {
        this.set('title', 'Add new source');
        this.okButtonNode.innerHTML = 'Add';
        this.edit = false;
      }
    },

    _okClick: function (evt) {
      console.debug('SourcesDialog::_okClick');
      evt.preventDefault();
      if (this._validate()) {
        if (this.edit) {
          this.emit('edit.source', {
            citation: this._editor.getContent(),
            id: this.source.id
          });
        } else {
          this.emit('add.source', {
            citation: this._editor.getContent()
          });
        }
        this.hide();
      } else {
        topic.publish('dGrowl', 'Please fill in all fields.', {
          'title': 'Invalid source',
          'sticky': false,
          'channel': 'info'
        });
      }
    },

    _cancelClick: function (evt) {
      console.debug('SourcesDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    reset: function () {
      this._editor.setContent('');
    },

    _validate: function () {
      return this._editor.getContent().trim() !== '';
    }
  });
});
