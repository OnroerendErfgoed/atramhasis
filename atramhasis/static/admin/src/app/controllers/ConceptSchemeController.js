/**
 * @module controllers/ConceptSchemeController
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/request/xhr',
  'dojo/store/JsonRest',
  'dojo/store/Cache',
  'dojo/store/Memory',
  'dojo/json'
], function (
  declare,
  lang,
  array,
  xhr,
  JsonRest,
  Cache,
  Memory,
  json
) {
  return declare( null, {

    conceptSchemeList: null,
    externalSchemeStore: null,
    _target: '/conceptschemes',
    _stores: {},


    constructor: function(args) {
      console.debug('ConceptSchemeController::constructor');
      declare.safeMixin(this, args);
      this.conceptSchemeList = [];
    },

    getConceptSchemes: function(){
      console.debug('ConceptSchemeController::getConceptSchemes');
      return xhr.get(this._target, {
        handleAs: 'json',
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
      })
    },

    getConceptScheme: function(id) {
      console.debug('ConceptSchemeController::getConceptScheme', id);
      return xhr.get(this._target + '/' + id, {
        handleAs: 'json',
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
      })
    },

    editConceptScheme: function(concept){
      console.debug('ConceptSchemeController::editConceptScheme', concept);
      var jData = json.stringify(concept);
      return xhr(this._target + '/' + concept.id,
        {
          handleAs: "json",
          method: "PUT",
          data: jData,
          headers:{'Content-Type': 'application/json', "Accept": "application/json"}
        });
    },

    loadConceptSchemeStores: function() {
      console.debug('ConceptSchemeController::loadConceptSchemeStores');
      return this.getConceptSchemes().then(lang.hitch(this, function (schemes) {
        var externalSchemelist = [];
        array.forEach(schemes, lang.hitch(this, function (scheme) {
          if(array.indexOf(scheme.subject, 'external') == -1){
            this.conceptSchemeList.push({name: scheme.label, id: scheme.id});
            //this.stores[scheme.id] = new JsonRest({
            //  'target': this._target + '/' + scheme.id + '/c/',
            //  'accepts': 'application/json'
            //});
          }else{
            externalSchemelist.push(scheme);
          }
        }));
        //this.externalSchemeStore = new Memory({
        //  idProperty: "id",
        //  data: externalSchemelist
        //});
      }))
    },

    getConceptSchemeTree: function(scheme) {
      var myStore = new Cache(new JsonRest({
        target: "/conceptschemes/" + scheme + "/tree",
        getChildren: function (object) {
          return object.children || [];
        }
      }), new Memory());
      return myStore;
    }
  })
});

