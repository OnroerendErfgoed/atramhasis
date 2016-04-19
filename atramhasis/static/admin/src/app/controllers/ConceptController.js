/**
 * @module controllers/ConceptController
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/request/xhr',
  'dojo/Deferred',
  'dstore/Rest'
], function (
  declare,
  lang,
  array,
  xhr,
  Deferred,
  Rest
) {
  return declare( null, {

    _stores: {},
    _target: '/conceptschemes/{schemeId}/c/',

    constructor: function(args) {
      console.debug('ConceptController::constructor');
      declare.safeMixin(this, args);
    },

    getConcept: function(schemeId, id) {
      console.debug('ConceptController::getConcept', schemeId, id);
      var deferred = new Deferred();
      var url = this._target.replace('{schemeId}', schemeId) + id;
      xhr.get(url, {
        handleAs: 'json',
        headers:{'Accept': 'application/json'}
      }).then(
        lang.hitch(this,function(data){
          deferred.resolve(data);
        }),
        function(err){
          console.error(err);
          if (err.response && err.response.data && err.response.data.message) {
            deferred.reject(err.response.data.message);
          }
          else {
            deferred.reject(err);
          }
        }
      );
      return deferred;
    },

    getConceptStore: function (schemeId) {
      console.debug('ConceptController::getConceptStore', schemeId);
      //check if store has been cached already
      if( !(schemeId in this._stores) ){
        this._stores[schemeId] = new Rest({
          target: this._target.replace('{schemeId}', schemeId),
          idProperty: 'id',
          sortParam: 'sort',
          useRangeHeaders: true
        });
      }
      return this._stores[schemeId];
    },

    saveConcept: function(concept) {
      console.debug('ConceptController::saveConcept', concept);

    }
  })
});

