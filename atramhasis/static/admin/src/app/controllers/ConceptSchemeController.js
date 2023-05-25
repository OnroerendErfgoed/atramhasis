/**
 * @module controllers/ConceptSchemeController
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/request/xhr',
  'dojo/Deferred',
  'dojo/store/JsonRest',
  'dojo/store/Cache',
  'dojo/store/Memory',
  'dstore/Memory',
  'dojo/json'
], function (
  declare,
  lang,
  array,
  xhr,
  Deferred,
  JsonRest,
  Cache,
  Memory,
  dMemory,
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
      });
    },

    getConceptScheme: function(id) {
      console.debug('ConceptSchemeController::getConceptScheme', id);
      return xhr.get(this._target + '/' + id, {
        handleAs: 'json',
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
      });
    },


    getConceptSchemeFromList: function(id) {
      console.debug('ConceptSchemeController::getConceptSchemeFromList', id);
      var conceptschemeList = array.filter(this.conceptSchemeList, function(item){
        return item.id === id;
      });
      return conceptschemeList.length > 0 ? conceptschemeList[0] : null;
    },

    editConceptScheme: function(concept){
      console.debug('ConceptSchemeController::editConceptScheme', concept);
      var jData = json.stringify(concept);
      return xhr(this._target + '/' + concept.id,
        {
          handleAs: "json",
          method: "PUT",
          data: jData,
          headers:{'Content-Type': 'application/json', 'Accept': "application/json"}
        });
    },

    loadConceptSchemeStores: function() {
      console.debug('ConceptSchemeController::loadConceptSchemeStores');
      return this.getConceptSchemes().then(lang.hitch(this, function (schemes) {
        var externalSchemelist = [];
        array.forEach(schemes, lang.hitch(this, function (scheme) {
          if (!scheme.label) {
            scheme.label = scheme.uri;
          }
          if (array.indexOf(scheme.subject, 'external') === -1) {
            this.conceptSchemeList.push(scheme);
          } else {
            externalSchemelist.push(scheme);
          }
        }));
        this.externalSchemeStore = new dMemory({
          idProperty: 'id',
          data: externalSchemelist
        });
      }));
    },

    getConceptSchemeTree: function(scheme) {
      return new Cache(new JsonRest({
        target: "/conceptschemes/" + scheme + "/tree",
        getChildren: function (object) {
          return object.children || [];
        }
      }), new Memory());
    },

    getMatch: function (uri, type) {
      var self = this;
      return xhr.get('/uris/' + uri, {
        handleAs: "json",
        headers: {'Accept' : 'application/json'}
      }).then(function(data){
        var id = data.id;
        var scheme = data.concept_scheme.id;
        var call = self.getConcept(scheme, uri);
        return call.then(function(concept) {
          return {
            type: type,
            data: {
              id: id,
              label: self._getPrefLabel(concept.labels, 'en'),
              uri: uri
            }
          };
        }, function(err){
          console.error(err);
          throw err;
        });
      }, function(err){
        console.error(err);
        throw err;
      });
    },

    getMergeMatch: function (uri) {
      var self = this;
      return xhr.get('/uris/' + uri, {
        handleAs: "json",
        headers: {'Accept' : 'application/json'}
      }).then(function(data){
        var id = data.id;
        var scheme = data.concept_scheme.id;
        var call = self.getConcept(scheme, uri);
        return call.then(function(concept) {
          return {
            labels: concept.labels,
            notes: concept.notes
          };
        }, function(err){
          console.error(err);
          throw err;
        });
      }, function(err){
        console.error(err);
        throw err;
      });
    },

    getConcept: function (scheme, uri) {
      var deferred = new Deferred();

      var pathArray =  uri.split('/');
      var id = pathArray.pop();
      if (!scheme || !id) {
        deferred.reject("Malformed external scheme URI");
      }

      var url = "/conceptschemes/" + scheme + "/c/" + id;

      xhr.get(url, {
        handleAs: "json",
        headers: {'Accept' : 'application/json'}
      }).then(
        function (c) {
          var clone = {
            label: c.label,
            labels: c.labels,
            type: c.type,
            notes: c.notes
          };
          if (c.type != 'collection') {
            clone.matches = {
              exact: [uri]
            };
          }
          deferred.resolve(clone);
        },
        function (err) {
          deferred.reject(err);
        }
      );

      return deferred;
    },

    _getPrefLabel: function (labels, lang) {
      var prefLabels = array.filter(labels, function(label) {
        return label.type == 'prefLabel';
      });
      if (prefLabels.length == 0) {
        return labels[0].label;
      }

      var correctlangLabels = array.filter(labels, function(label) {
        return label.language == lang;
      });
      if (correctlangLabels.length == 0) {
        return prefLabels[0].label;
      }
      else {
        return correctlangLabels[0].label;
      }
    },

    getExternalSchemeStore: function() {
      if (this.externalSchemeStore) {
        return this.externalSchemeStore;
      }
      return null;
    },

    searchForConcepts: function (scheme, value) {
      var url = '/conceptschemes/' + scheme + '/c?label=' + value + '&type=all&sort=+label';
      return xhr.get(url, {
        handleAs: "json",
        headers: {'Accept' : 'application/json'}
      });
      //  .then(function(data){
      //  self._externalConceptList.refresh();
      //  self._externalConceptList.renderArray(data);
      //}, function(err){
      //  console.error(err);
      //});
    }
  });
});

