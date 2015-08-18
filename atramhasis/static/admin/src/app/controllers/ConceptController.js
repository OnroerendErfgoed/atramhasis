/**
 * @module controllers/ConceptController
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
    return declare(null, /** @lends module:controllers/ConceptController# */ {

        _target: '/conceptschemes',

        /**
         * Controller voor het beheer (ophalen/editeren) van de Concepts.
         * @constructs
         * @param args Options
         */
        constructor: function(args) {
            console.debug('ConceptController::constructor');
            declare.safeMixin(this, args);
        },

        getConcepts: function(){
            console.debug('ConceptController::getConcepts');
            return xhr.get(this._target, {
                handleAs: 'json',
                headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
            })
        },

        getConcept: function(id) {
            console.debug('ConceptController::getConcept', id);
            return xhr.get(this._target + '/' + id, {
                handleAs: 'json',
                headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
            })
        },

        editConceptScheme: function(concept){
            console.debug('ConceptController::editConceptScheme', concept);
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

