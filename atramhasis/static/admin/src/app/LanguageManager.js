define([
    'dijit/_WidgetBase',
    'dojo/_base/declare',
    'dojo/store/JsonRest'
], function (WidgetBase, declare, JsonRest) {
    return declare([WidgetBase], {

        _languageStore: null,

        postCreate: function () {
            this.inherited(arguments);

            this._languageStore = new JsonRest({
                'target': '/languages',
                'idProperty': 'id',
                'accepts': 'application/json'
            });
            this._languageStore.get('nl').then(function(item){
                console.log(item);
            });
        },

        startup: function () {
            this.inherited(arguments);
        },

        showDialog: function () {
            console.log("open dialog");
             this._languageStore.add({
                name: "Afrikaans"
              }, {
                id: "af"
              });
        }
    });
});
