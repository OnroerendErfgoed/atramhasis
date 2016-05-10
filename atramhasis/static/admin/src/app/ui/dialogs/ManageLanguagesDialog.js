define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/topic',
  'dojo/text!./templates/ManageLanguagesDialog.html',
  '../../utils/DomUtils'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  topic,
  template,
  DomUtils
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'manage-languages-dialog',
    title: 'Manage languages',
    languageController: null,
    _langStore: null,
    _langGrid: null,

    postCreate: function () {
      this.inherited(arguments);
    },

    startup: function () {
      this.inherited(arguments);

    },

    hide: function () {
      this.inherited(arguments);
      //this._reset();
    },

    show: function () {
      this.inherited(arguments);
      //this._reset();
    },

    _okClick: function (evt) {
      console.debug('LanguagesDialog::_okClick');
      evt.preventDefault();
      if (this._validate()) {
        //this.emit('add.label', {
        //
        //});
      }
    },

    _cancelClick: function (evt) {
      console.debug('LanguagesDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    _reset: function () {

    },

    _validate: function () {
      return true;
    }
  });
});
