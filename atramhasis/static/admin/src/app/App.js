/**
 * Main application widget.
 * @module App
 * @see module:App
 */
define([
  'dojo/_base/declare',
  'dijit/_WidgetBase',
  './ui/AppUi'
], function (declare, WidgetBase, AppUi) {
  return declare([WidgetBase], {

    appConfig: null,

    _controllers: null,

    /**
     * Standard widget function.
     * @public
     */
    postCreate: function () {
      this.inherited(arguments);
      console.debug('App::postCreate');
      this._controllers = {};

    },

    /**
     * Standard widget function.
     * @public
     */
    startup: function () {
      this.inherited(arguments);
      console.debug('App::startup');

      new AppUi({
        loadingContainer: this.appConfig.loadingContainer
      }, this.appConfig.appContainer).startup();
    }
  });
});
