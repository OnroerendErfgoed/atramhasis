define(
    [
        "dojo/_base/declare",
        "dojo/_base/lang",
        "dojo/_base/array",
        "dojo/request",
        "dojo/store/JsonRest",
        "dojo/store/Memory"
    ],
    function (declare, lang, array, request, JsonRest, Memory) {
        return declare(null,
            {

                schemelist: [],
                externalSchemeStore: null,
                stores: {},

                constructor: function (/*Object*/ args) {
                    declare.safeMixin(this, args);
                    request.get(
                        '/conceptschemes',
                        {'handleAs': 'json'}
                    ).then(lang.hitch(this, function (schemes) {
                            var externalSchemelist = [];
                            array.forEach(schemes, lang.hitch(this, function (scheme) {
                                if(array.indexOf(scheme.subject, 'external') == -1){
                                    this.schemelist.push({name: scheme.id, id: scheme.id});
                                    this.stores[scheme.id] = new JsonRest({
                                        'target': '/conceptschemes/' + scheme.id + '/c/'
                                    });
                                }else{
                                    externalSchemelist.push(scheme);
                                }
                            }));
                            this.externalSchemeStore = new Memory({
                                idProperty: "id",
                                data: externalSchemelist
                            });
                        }))
                }

            }
        );
    });
