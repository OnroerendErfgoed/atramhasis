define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/topic',
  'dojo/dom-construct',
  'dojo/text!./templates/CreateSchemeDialog.html',
  '../../utils/DomUtils'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  topic,
  domConstruct,
  template,
  DomUtils
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'create-scheme-dialog',
    title: 'Create Concept scheme',
    labelElement: null,
    typeList: null,
    langList: null,

    startup: function () {
      this.inherited(arguments);
    },

    setData: function(label, uri) {
      this.labelInputNode.value = label
      this.uriInputNode.value = uri
    },

    hide: function () {
      this.inherited(arguments);
      this.reset();
    },

    show: function (label) {
      this.inherited(arguments);
      this.reset();
      this.set('title', 'Create new conceptscheme');
      this.okButtonNode.innerHTML = 'Create';
    },

    _okClick: function (evt) {
      console.debug('CreateSchemeDialog::_okClick');
      evt.preventDefault();
      if (this._validate()) {
        this.emit('scheme.create', { scheme: {
          label: this.labelInputNode.value.trim(),
          uri: this.uriInputNode.value.trim(),
        }
        });

        this.hide();
      } else {
        topic.publish('dGrowl', 'Please fill in all fields.', {
          'title': 'Invalid label',
          'sticky': false,
          'channel': 'info'
        });
      }
    },

    _cancelClick: function (evt) {
      console.debug('CreateSchemeDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    reset: function () {
      this.labelInputNode.value = '';
      this.uriInputNode.value = '';
    },

    _validate: function () {
      return this.labelInputNode.value.trim() !== '';
    }
  });
});
