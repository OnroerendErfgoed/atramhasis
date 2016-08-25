define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/topic',
  'dojo/text!./templates/LanguageDialog.html',
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
    baseClass: 'language-dialog',
    title: 'Edit language',
    language: null,
    edit: true,

    postCreate: function () {
      this.inherited(arguments);
    },

    startup: function () {
      this.inherited(arguments);

    },

    setData: function(language) {
      console.log(language);
      this.codeInputNode.value = language.id;
      this.descriptionInputNode.value = language.name;
    },

    hide: function () {
      this.inherited(arguments);
      this.reset();
    },

    show: function (language) {
      this.inherited(arguments);
      this.reset();
      if (language) {
        this.setData(language);
        this.set('title', 'Edit language');
        this.okButtonNode.innerHTML = 'Edit';
        this.edit = true;
        this.language = language;
      } else {
        this.set('title', 'Add new language');
        this.okButtonNode.innerHTML = 'Add';
        this.edit = false;
      }
    },

    _okClick: function (evt) {
      console.debug('languageDialog::_okClick');
      evt.preventDefault();
      if (this._validate()) {
        this.language.id = this.codeInputNode.value;
        this.language.name = this.descriptionInputNode.value;
        if (this.edit) {
          this.emit('edit.language', {
            language: this.language
          });
        } else {
          this.emit('add.language', {
            language: this.language
          });
        }
        this.hide();
      } else {
        topic.publish('dGrowl', 'Please fill in at least a language code.', {
          'title': 'Invalid language',
          'sticky': false,
          'channel': 'info'
        });
      }
    },

    _cancelClick: function (evt) {
      console.debug('languageDialog::_cancelClick');
      evt ? evt.preventDefault() : null;
      this.hide();
    },

    reset: function () {
      this.codeInputNode.value = '';
      this.descriptionInputNode.value = '';
    },

    _validate: function () {
      return (this.codeInputNode.value.trim() !== null && this.codeInputNode.value.trim() !== '');
    }
  });
});
