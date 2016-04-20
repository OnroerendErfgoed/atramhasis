/**
 * Header layout template.
 * @module ui/views/Header
 */
define([
  'dojo/_base/declare',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/Header.html',
  'dojo/Evented'
], function (
  declare,
  _WidgetBase,
  _TemplatedMixin,
  template,
  Evented
) {
  return declare([_WidgetBase, _TemplatedMixin, Evented], {

    baseClass: 'appHeader',
    templateString: template,
    title: null,
    staticAppPath: null,

    /**
     * Standaard widget functie.
     */
    postCreate: function () {
      this.inherited(arguments);
      console.debug('Header::postCreate');
    },

    /**
     * Standaard widget functie.
     * Bouwt de header op.
     */
    startup: function () {
      console.debug('Header::startup');
      this.inherited(arguments);
    },

    /**
     * Zet de titel van de applicatie.
     * @param {string} title Nieuwe titel voor de applicatie
     */
    setTitle: function (title) {
      this.titleNode.innerHTML = title;
    },

    /* UI actions */
    /**
     * Stuur een event om het menu te tonen.
     */
    _toggleMenu: function (e) {
      e ? e.preventDefault() : null;
      this.emit('toggleMenu');
    },

    /**
     * Overwrite van standaard widget functie
     * @param e Event
     */
    destroy: function(e) {
      e ? e.preventDefault() : null;
      console.log('Header::destroy');
    }

  });
});
