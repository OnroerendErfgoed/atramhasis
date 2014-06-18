define([
    'dojo/has', 'require',
    "dojo/store/Memory", "dojo/store/Cache", "dojo/store/JsonRest", "dojo/store/Observable",
    'dojo/_base/sniff'
], function (
        has, require,
        Memory, Cache, JsonRest, Observable
    ) {
    var app = window.app = {};

    if (has('host-browser')) {

        require([ './App', 'dojo/domReady!' ], function (App) {
            app.main = new App().placeAt("appDiv");

            app.main.startup();
        })
    } else {
            console.log("server");
        }
    });