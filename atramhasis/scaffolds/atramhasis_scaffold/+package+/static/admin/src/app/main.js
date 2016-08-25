/**
 * Main module. Starts the App module.
 * @module main
 * @see module:App
 */

define([
  './App',
  'dojo/dom',
  'dojo/domReady!'
], function (App, dom) {

  var appConfig = {
    appContainer: dom.byId('appDiv'),
    loadingContainer: dom.byId('loadingOverlay'),
    staticAppPath: staticAppPath
  };

  new App({appConfig: appConfig}).startup();

});
