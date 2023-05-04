define([
  'dojo/_base/declare',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dijit/Dialog',
  'dojo/topic',
  'dojo/_base/lang',
  'dojo/query',
  'dojo/on',
  'dojo/when',
  'dojo/_base/array',
  'dojo/dom-construct',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/DijitRegistry',
  'dgrid/extensions/ColumnResizer',
  'dojo/text!./templates/ManageProvidersDialog.html',
  'dijit/ConfirmDialog',
  '../../utils/DomUtils',
  './LanguageDialog',
  'dojo/NodeList-manipulate'
], function (
  declare,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  Dialog,
  topic,
  lang,
  query,
  on,
  when,
  array,
  domConstruct,
  OnDemandGrid,
  DijitRegistry,
  ColumnResizer,
  template,
  ConfirmDialog,
  DomUtils,
  LanguageDialog
) {
  return declare([Dialog, _TemplatedMixin, _WidgetsInTemplateMixin], {

    templateString: template,
    parentNode: null,
    baseClass: 'manage-providers-dialog',
    title: 'Manage providers',
    providerController: null,
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
    },

    show: function () {
      this.inherited(arguments);
      this._reset();
    },

    _cancelClick: function (evt) {
      console.debug('ProvidersDialog::_cancelClick');
      evt.preventDefault();
      this.hide();
    },

    _reset: function () {
    }
  });
});
