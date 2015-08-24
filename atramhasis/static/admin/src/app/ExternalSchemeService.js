define([
    "dojo/_base/declare",
    "dijit/_WidgetBase",
    "dojo/request/xhr",
    "dojo/Deferred",
    "dojo/_base/array",
    "dojo/json",
    "dojo/when"

], function (declare, WidgetBase, xhr, Deferred, array, JSON, when) {
    return declare([WidgetBase], {

        thesauri: null,

        matchTypes: [
            {label: "Broad", value: "broad"},
            {label: "Close", value: "close"},
            {label: "Exact", value: "exact"},
            {label: "Narrow", value: "narrow"},
            {label: "Related", value: "related"}
        ],

        postCreate: function () {
            this.inherited(arguments);
        },

        startup: function () {
            this.inherited(arguments);
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
                        }
                    }
                    deferred.resolve(clone);
                },
                function (err) {
                    deferred.reject(err);
                }
            );

            return deferred;
        },

        getScheme: function (schemeUrl) {
            return this.thesauri.externalSchemeStore.query({uri: schemeUrl})[0];
        },

        searchConcepts: function (scheme, text) {
            var url = "/conceptschemes/" + scheme + "/c?label=" + text + "&type=all&sort=+label";
            return xhr.get(url, {
                handleAs: "json",
                headers: {'Accept' : 'application/json'}
            })
        },

        getExternalSchemeStore: function () {
            return this.thesauri.externalSchemeStore;
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
        }
    });
});