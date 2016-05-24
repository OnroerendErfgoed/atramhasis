/**
 * @module controllers/ConceptController
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/request/xhr',
  'dojo/request',
  'dojo/Deferred',
  'dojo/json',
  'dstore/Rest'
], function (
  declare,
  lang,
  array,
  xhr,
  request,
  Deferred,
  json,
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

    saveConcept: function(concept, schemeId, method) {
      console.debug('ConceptController::saveConcept', concept);

      var url = this._target.replace('{schemeId}', schemeId);

      if (method === 'PUT') {
        url = this._target.replace('{schemeId}', schemeId) + concept.id;
      }

      return request(url, {
        method: method,
        data: json.stringify(concept),
        handleAs: 'json',
        headers: {
          'Accept': 'application/json',
          'Content-type': 'application/json',
          'X-Requested-With': ''
        }
      });
    },

    deleteConcept: function(concept, schemeId) {
      console.debug('ConceptController::deleteConcept', concept);
      var url = this._target.replace('{schemeId}', schemeId) + concept.id;
      return request(url, {
        method: 'DELETE',
        handleAs: 'json',
        headers: {
          'Accept': 'application/json',
          'Content-type': 'application/json',
          'X-Requested-With': ''
        }
      });
    },

    getConceptByUri: function(uri) {
      return request(uri, {
        method: 'GET',
        handleAs: 'json',
        headers: {
          'Accept': 'application/json',
          'Content-type': 'application/json',
          'X-Requested-With': ''
        }
      });
    }
  })
});

