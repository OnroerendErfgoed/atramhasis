/**
 * @module controllers/ProviderController
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/request/xhr',
  'dstore/Rest',
  'dstore/Trackable'
], function (
  declare,
  lang,
  array,
  xhr,
  Rest,
  Trackable
) {
  return declare( null, {

    _baseUrl: '',
    _target: '/providers',
    _providerStore: null,
    providerList: null,
    TrackableRest: null,

    constructor: function(args) {
      console.debug('ProviderController::constructor');
      declare.safeMixin(this, args);
      this.providerList = [];
      this.TrackableRest = declare([ Rest, Trackable ]);
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

    getProviderStore: function () {
      console.debug('ProviderController::getProviderStore');
      if (!this._providerStore) {
        this._providerStore = new this.TrackableRest({
          target: this._baseUrl + this._target,
          idProperty: 'id',
          sortParam: 'sort',
          useRangeHeaders: true,
          accepts: 'application/json'
        });
      }
      return this._providerStore;
    },

    loadProviders: function() {
      console.debug('ProviderController::loadProviders');
      return this.getProviders().then(lang.hitch(this, function (providers) {
        this.providerList = providers;
      }));
    }
  });
});

