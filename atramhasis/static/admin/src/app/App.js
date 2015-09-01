/**
 * Main application widget.
 * @module App
 * @see module:App
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/promise/all',
  'dijit/_WidgetBase',
  './ui/AppUi',
  './controllers/ConceptSchemeController',
  './controllers/ConceptController',
  'dGrowl'
], function (declare, lang, all, WidgetBase, AppUi, ConceptSchemeController, ConceptController, dGrowl) {
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

      this._controllers.conceptSchemeController = new ConceptSchemeController({});
      this._controllers.conceptController = new ConceptController({});

      //Start message handler
      new dGrowl({
        'channels':[
          {'name':'info','pos':3},
          {'name':'error', 'pos':1},
          {'name':'warn', 'pos':2}
        ]
      });

    },

    /**
     * Standard widget function.
     * @public
     */
    startup: function () {
      this.inherited(arguments);
      console.debug('App::startup');

      var conceptSchemePromise = this._controllers.conceptSchemeController.loadConceptSchemeStores();

        all({
          conceptScheme: conceptSchemePromise
        }).then(
          lang.hitch(this, function(results) {
            new AppUi({
              loadingContainer: this.appConfig.loadingContainer,
              staticAppPath: this.appConfig.staticAppPath,
              conceptSchemeController: this._controllers.conceptSchemeController,
              conceptController: this._controllers.conceptController
            }, this.appConfig.appContainer).startup();
          }),
          lang.hitch(this, function(error) {
            console.error(error);
            window.alert("Startup error: \n\n" +
              "There was a problem connecting to the backend services, the application cannot be started.");
          })
        );
    }
  });
});
