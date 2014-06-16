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

            app.schemeStore = new Observable (new Cache (new JsonRest ({
                target: "/conceptschemes"
            }), new Memory ()));

            app.typeStore = new Memory({
                data: [
                    {name:"All", id:"all"},
                    {name:"Concepts", id:"concept"},
                    {name:"Collections", id:"collection"}
                ]
            });

            app.conceptstores = {};
            app.conceptstores.treeStore = new Observable (new Cache (new JsonRest ({
                target: "/conceptschemes/TREES/c/"
            }), new Memory ()));

            app.main.conceptschemes = app.schemeStore;
            app.main.concepttypes = app.typeStore;
            app.main.tree = app.typeStore;


            app.main.startup();
        })
    } else {
            console.log("server");
        }
    });