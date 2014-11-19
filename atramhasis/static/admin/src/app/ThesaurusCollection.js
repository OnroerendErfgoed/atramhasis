define(
    [
        "dojo/_base/declare",
        "dojo/_base/lang",
        "dojo/_base/array",
        "dojo/request",
        "dojo/store/JsonRest"
    ],
    function (declare, lang, array, request, JsonRest) {
        return declare(null,
            {

                schemelist: [],
                externalSchemelist: [],
                stores: {},

                constructor: function (/*Object*/ args) {
                    declare.safeMixin(this, args);
                    request.get(
                        '/conceptschemes',
                        {'handleAs': 'json'}
                    ).then(lang.hitch(this, function (schemes) {
                            array.forEach(schemes, lang.hitch(this, function (scheme) {
                                if(array.indexOf(scheme.subject, 'external') == -1){
                                    this.schemelist.push({name: scheme.id, id: scheme.id});
                                }else{
                                    this.externalSchemelist.push({name: scheme.id, id: scheme.id});
                                }
                                this.stores[scheme.id] = new JsonRest({
                                    'target': '/conceptschemes/' + scheme.id + '/c/'
                                });
                            }));
                        }))
                }

            }
        );
    });
