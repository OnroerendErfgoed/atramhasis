define([
  'dojo/_base/declare',
  'dstore/Rest',
  'dstore/Trackable'
], function (
  declare,
  Rest,
  Trackable
) {
  return declare(null, {

    _target: '/languages',
    TrackableRest: null,
    _baseUrl: '',
    _langStore: null,

    constructor: function (args) {
      console.debug('LangController::constructor');
      declare.safeMixin(this, args);
      this.TrackableRest = declare([ Rest, Trackable ]);
    },

    getLanguageStore: function () {
      //check if store has been cached already
      if (!this._langStore) {
        this._langStore = new this.TrackableRest({
          target: this._baseUrl + this._target,
          idProperty: 'id',
          sortParam: 'sort',
          useRangeHeaders: true,
          accepts: 'application/json'
        });
      }
      return this._langStore;
    }

  });
});