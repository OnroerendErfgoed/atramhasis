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

        getMatch: function (uri, type, importscheme) {
            var pathArray =  uri.split('/');
            var id = pathArray.pop();
            var testUrl = pathArray.pop(); //remove 'concept' from url
            if (!testUrl) throw  "Malformed URI";

            var schemeUrl = pathArray.join('/');
            var scheme = importscheme ? importscheme : this.getScheme(schemeUrl);
            if (!scheme) throw  "Malformed external scheme URI";

            var call = this.getConcept(scheme, uri);
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

        getConcept: function (scheme, uri) {
            var pathArray =  uri.split('/');
            var id = pathArray.pop();
            if (!scheme || !id) throw  "Malformed external scheme URI";
            var url = "/conceptschemes/" + scheme + "/c/" + id;

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