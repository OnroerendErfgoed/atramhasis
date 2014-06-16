define(
    [
        "dojo/_base/declare",
        "dojo/_base/lang",
        "dojo/_base/array",
        "dojo/request",
        "dojo/store/JsonRest",
        "dojo/store/Memory",
        "dojo/store/Cache",
        "dojo/store/Observable",
        "dojo/topic"
    ],
    function (
        declare,
        lang,
        array,
        request,
        JsonRest,
        Memory,
        Cache,
        Observable,
        topic) {
        return declare( null,
            {

                stores: {},

                constructor: function (/*Object*/ args) {
                    declare.safeMixin(this, args);
                    request.get(
                        '/conceptschemes',
                        {'handleAs': 'json'}
                    ).then(lang.hitch(this,function(schemes) {
                            array.forEach(schemes, lang.hitch(this, function(scheme) {
                                var store = new JsonRest({
                                    'target': '/conceptschemes/' + scheme.id + '/c/'
                                });
                                //var mstore = new Memory();
                                //var store = new Cache(rstore, mstore);
                                this.stores[scheme.id] = store;
                            }));
                        }));
                }

            }
        );
    });
