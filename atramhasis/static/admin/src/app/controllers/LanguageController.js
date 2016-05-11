define([
  'dojo/_base/declare',
  'dstore/Rest',
  'dstore/Trackable',
  'dstore/Cache',
  'dstore/Memory',
  'dojo/topic'
], function (
  declare,
  Rest,
  Trackable,
  Cache,
  Memory,
  topic
) {
  return declare(null, {

    _target: '/languages',
    TrackableRest: null,
    _baseUrl: '',
    _langStore: null,
    _langList: null,

    constructor: function (args) {
      console.debug('LangController::constructor');
      declare.safeMixin(this, args);
      this.TrackableRest = declare([ Rest, Trackable ]);
    },

    getLanguageStore: function () {
      if (!this._langStore) {
        var trackStore = new this.TrackableRest({
          target: this._baseUrl + this._target,
          idProperty: 'id',
          sortParam: 'sort',
          useRangeHeaders: true,
          accepts: 'application/json'
        });
        this._langStore = Cache.create(trackStore, {
          cachingStore: new Memory(),
          isValidFetchCache: true
        });
      }
      return this._langStore;
    },

    updateLanguageStore: function() {
      // invalidate cache after add/remove and send event to update select lists
      this.getLanguageStore().invalidate();
      topic.publish('languages.updated');
    }
  });
});