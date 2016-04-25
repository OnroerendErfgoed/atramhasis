define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/text!./templates/NotesDialog.html',
  '../../utils/HtmlEditor',
  '../../utils/DomUtils'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  template,
  HtmlEditor,
  DomUtils
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'notes-dialog',
    title: 'Add note',
    typeList: null,
    langList: null,
    _editor: null,

    postCreate: function () {
      this.inherited(arguments);
      this._editor = new HtmlEditor({}, this.htmlEditorNode);
      DomUtils.addOptionsToSelect(this.typeSelectNode, {
        data: this.typeList,
        idProperty: 'value',
        labelProperty: 'label'
      });
      DomUtils.addOptionsToSelect(this.langSelectNode, {
        data: this.langList,
        idProperty: 'id',
        labelProperty: 'name'
      });
    },

    startup: function () {
      this.inherited(arguments);
      this._editor.startup();
      this._editor.addButtons(['emphasis', 'strong', 'link']);
      this._editor.setContent('blablabla');
    },

    hide: function () {
      this._reset();
      this.inherited(arguments);
    },

    _okClick: function (evt) {
      console.debug('NotesDialog::_okClick');
      evt.preventDefault();
      if (this._validate()) {
        //this.emit('ok', {
        //  auteur: this.auteurInput.value,
        //  node: this.parentNode
        //});
        this.hide();
      }
    },

    _cancelClick: function (evt) {
      console.debug('NotesDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    _reset: function () {
      //this.auteurInput.value = '';
    },

    _validate: function () {
      //return this.auteurInput.value.trim() !== '';
    }
  });
});
