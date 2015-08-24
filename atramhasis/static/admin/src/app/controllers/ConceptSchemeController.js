/**
 * @module controllers/ConceptSchemeController
 */
define([
    'dojo/_base/declare',
    'dojo/request/xhr',
    'dojo/json'
], function (
    declare,
    xhr,
    json
) {
    return declare(null, /** @lends module:controllers/ConceptSchemeController# */ {

        _target: '/conceptschemes',

        /**
         * Controller voor het beheer (ophalen/editeren) van de Concepts.
         * @constructs
         * @param args Options
         */
        constructor: function(args) {
            //console.debug('ConceptSchemeController::constructor');
            declare.safeMixin(this, args);
        },

        getConcepts: function(){
            //console.debug('ConceptSchemeController::getConcepts');
            return xhr.get(this._target, {
                handleAs: 'json',
                headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
            })
        },

        getConcept: function(id) {
            //console.debug('ConceptSchemeController::getConcept', id);
            return xhr.get(this._target + '/' + id, {
                handleAs: 'json',
                headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
            })
        },

        editConceptScheme: function(concept){
            //console.debug('ConceptSchemeController::editConceptScheme', concept);
            var jData = json.stringify(concept);
            return xhr(this._target + '/' + concept.id,
                {
                    handleAs: "json",
                    method: "PUT",
                    data: jData,
                    headers:{'Content-Type': 'application/json', "Accept": "application/json"}
                });
        }
    })
});

