define([
    'dijit/_WidgetBase',
    'dojo/_base/declare'
], function (WidgetBase, declare) {
    return declare([WidgetBase], {

        postCreate: function () {
            this.inherited(arguments);
        },

        startup: function () {
            this.inherited(arguments);
        },

        showDialog: function () {
            console.log("open dialog");
        }
    });
});
