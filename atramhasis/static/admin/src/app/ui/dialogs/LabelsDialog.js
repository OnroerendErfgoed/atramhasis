define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/topic',
  'dojo/dom-construct',
  'dojo/text!./templates/LabelsDialog.html',
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
    baseClass: 'labels-dialog',
    title: 'Add label',
    labelElement: null,
    typeList: null,
    langList: null,
    edit: false,

    postCreate: function () {
      this.inherited(arguments);
      DomUtils.addOptionsToSelect(this.typeSelectNode, {
        data: this.typeList,
        idProperty: 'value',
        labelProperty: 'label'
      });
      DomUtils.addOptionsToSelect(this.langSelectNode, {
        data: this.langList,
        idProperty: 'id',
        labelProperty: 'name',
        showId: true
      });
    },

    startup: function () {
      this.inherited(arguments);
    },

    setData: function(label) {
      this.labelInputNode.value = label.label
      this.langSelectNode.value = label.language;
      this.typeSelectNode.value = label.type;
    },

    hide: function () {
      this.inherited(arguments);
      this.reset();
    },

    show: function (label) {
      this.inherited(arguments);
      this.reset();
      if (label) {
        this.setData(label);
        this.set('title', 'Edit label');
        this.okButtonNode.innerHTML = 'Edit';
        this.edit = true;
        this.labelElement = label;
      } else {
        this.set('title', 'Add new label');
        this.okButtonNode.innerHTML = 'Add';
        this.edit = false;
      }
    },

    updateLanguages: function(langs) {
      // update languagelist and refresh select list
      this.langList = langs;
      domConstruct.empty(this.langSelectNode);
      DomUtils.addOptionsToSelect(this.langSelectNode, {
        data: this.langList,
        idProperty: 'id',
        labelProperty: 'name'
      });
    },

    _okClick: function (evt) {
      console.debug('LabelsDialog::_okClick');
      evt.preventDefault();
      if (this._validate()) {
        if (this.edit) {
          this.emit('edit.label', {
            label: this.labelInputNode.value.trim(),
            lang: this.langSelectNode.value,
            labelType: this.typeSelectNode.value,
            id: this.labelElement.id
          });
        } else {
          this.emit('add.label', {
            label: this.labelInputNode.value.trim(),
            lang: this.langSelectNode.value,
            labelType: this.typeSelectNode.value
          });
        }
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
      console.debug('LabelsDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    reset: function () {
      this.labelInputNode.value = '';
      this.langSelectNode.selectedIndex = 0;
      this.typeSelectNode.selectedIndex = 0;
    },

    _validate: function () {
      return this.labelInputNode.value.trim() !== '';
    }
  });
});
