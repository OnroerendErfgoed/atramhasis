/**
 * @module controllers/ConceptController
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/request/xhr',
  'dstore/Rest'
], function (declare, lang, array, xhr, Rest) {
  return declare( null, {

    _stores: {},
    _target: '/conceptschemes/{schemeId}/c/',

    constructor: function(args) {
      console.debug('ConceptController::constructor');
      declare.safeMixin(this, args);
    },

    getConcepts: function(){
      console.debug('ConceptController::getConcepts');
    },

    getConcept: function(id) {
      console.debug('ConceptController::getConcept', id);
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
    }
  })
});

