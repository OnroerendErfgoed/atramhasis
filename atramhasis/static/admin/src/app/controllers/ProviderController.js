/**
 * @module controllers/ProviderController
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/request/xhr'
], function (
  declare,
  lang,
  array,
  xhr
) {
  return declare( null, {

    _target: '/providers',
    providerList: null,

    constructor: function(args) {
      console.debug('ProviderController::constructor');
      declare.safeMixin(this, args);
      this.providerList = [];
    },

    getProviders: function() {
      console.debug('ProviderController::getProviders');
      return xhr.get(this._target, {
        handleAs: 'json',
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
      });
    },

    getProvider: function(uri) {
      console.debug('ProviderController::getProvider', uri);
      var providerList = array.filter(this.providerList, function(item){
        return item.conceptscheme_uri === uri;
      });
      return providerList.length > 0 ? providerList[0] : null;
    },

    loadProviders: function() {
      console.debug('ProviderController::loadProviders');
      return this.getProviders().then(lang.hitch(this, function (providers) {
        this.providerList = providers;
      }));
    }
  });
});

