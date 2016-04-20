/**
 * Footer layout template.
 * @module ui/views/Footer
 */
define([
  'dojo/_base/declare',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/Footer.html'
], function (
  declare,
  _WidgetBase,
  _TemplatedMixin,
  template
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'appFooter',

    /**
     * Standaard widget functie.
     */
    postCreate: function () {
      this.inherited(arguments);
      console.debug('Footer::postCreate');
    },

    /**
     * Standaard widget functie.
     */
    startup: function () {
      this.inherited(arguments);
      console.debug('Footer::startup');
    }

  });
});
