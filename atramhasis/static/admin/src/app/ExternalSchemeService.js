define([
    "dojo/_base/declare",
    "dijit/_WidgetBase",
    "dojo/request/xhr",
    "dojo/_base/array",
    "dojo/json",
    "dojo/when"

], function (declare, WidgetBase, xhr, array, JSON, when) {
    return declare([WidgetBase], {

        thesauri: null,

        postCreate: function () {
            this.inherited(arguments);
        },

        startup: function () {
            this.inherited(arguments);
        },

        getMatch: function (uri, type) {
            var pathArray =  uri.split('/');
            var id = pathArray.pop();
            var testUrl = pathArray.pop(); //remove 'concept' from url
            if (!testUrl) throw  "Malformed URI";

            var schemeUrl = pathArray.join('/');
            var scheme = this.getScheme(schemeUrl);
            if (!scheme) throw  "Malformed external scheme URI";
            var url = "/conceptschemes/" + scheme.id + "/c/" + id;

            var call = this.getConcept(uri);

            return call.then(function(concept) {
                var match = {
                    type: type,
                    data: {
                        id: id,
                        label: concept.labels[0].label,
                        uri: uri
                    }
                };
                return match;
            }, function(err){
                console.error(err);
                throw err;
            });
        },

        getConcept: function (uri) {
            var pathArray =  uri.split('/');
            var id = pathArray.pop();
            var testUrl = pathArray.pop(); //remove 'concept' from url
            if (!testUrl) throw  "Malformed URI";

            var schemeUrl = pathArray.join('/');
            var scheme = this.getScheme(schemeUrl);
            if (!scheme) throw  "Malformed external scheme URI";
            var url = "/conceptschemes/" + scheme.id + "/c/" + id;

            return xhr.get(url, {
                handleAs: "json",
                headers: {'Accept' : 'application/json'}
            });
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
        }
    });
});