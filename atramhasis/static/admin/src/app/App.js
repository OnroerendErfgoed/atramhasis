define([
    "dojo/_base/declare",
    "dojo/on",
    "dojo/topic",
    "dojo/_base/lang",
    "dojo/store/Memory",
    "dojo/cookie",
    "dojo/fx/Toggler",
    "dojo/dom",
    "dojo/request",
    "dijit/registry",
    "dijit/form/FilteringSelect",
    "dijit/_Widget",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",

    "dojo/text!./templates/App.html",

    "dijit/form/ComboBox", "dijit/form/Button", "dijit/Dialog",

    "./FilteredGrid",
    "./ConceptDetail",
    "./ThesaurusCollection",
    "./ConceptForm",
//    "dojo/text!./templates/ConceptForm.html",

    "dijit/layout/ContentPane",
    "dijit/layout/TabContainer",
    "dijit/layout/BorderContainer"


], function(
    declare, on, topic, lang,

    Memory,
    cookie,
    Toggler,
    dom,
    request,
    registry,
    FilteringSelect,
    _Widget,
    _TemplatedMixin,
    _WidgetsInTemplateMixin,

    template,

    ComboBox, Button, Dialog,

    FilteredGrid, ConceptDetail,
    ThesaurusCollection,
    ConceptForm,

    ContentPane, TabContainer
    ){
    return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {

        templateString: template,
        thesauri: null,
        currentScheme: null,

        postMixInProperties: function () {
            this.inherited(arguments);

            console.log('postMixInProperties', arguments);
        },

        buildRendering: function () {
            this.inherited(arguments);

            console.log('buildRendering', arguments);
        },

        postCreate: function () {
            this.inherited(arguments);
            console.log('postCreate', arguments);
            this.thesauri = new ThesaurusCollection();
        },

        startup: function () {
            this.inherited(arguments);
            console.log('startup', arguments);
            var self = this;

      /*      var schemeCombo = new ComboBox({
                id: "schemeSelect",
                name: "scheme",
                store: new Memory({ data: this.thesauri.schemelist }),
                searchAttr: "id",
                placeHolder: 'select thesaurus'
            }, "selectNode");*/

            var schemeFileteringSelect=new FilteringSelect({
                id: "schemeSelect",
                name: "scheme",
                store: new Memory({ data: this.thesauri.schemelist }),
                searchAttr: "id",
                placeHolder: 'select thesaurus'
            },"selectNode");

            var filteredGrid = new FilteredGrid({
                id: "conceptGrid"
            }, "filteredGridNode");
            filteredGrid.startup();

            var conceptDialog = new Dialog({
                id: 'conceptDialog',
                content:new ConceptForm(),
                title:"Add concept",
                style: "width: 500px"
            }).placeAt(document.body);




            var tc = registry.byId("center");

            var cpwelcome = new ContentPane({
                title: "Welcome",
                content: "[welcome]"
            });
            tc.addChild(cpwelcome);
            tc.startup();


             var addConceptButton = new Button({
                label: "Add concept or collection",
                disabled:"disabled"
            }, "addConceptNode");
            on(schemeFileteringSelect, "change", function(e){

                if(e)
                {
                    console.log("on schemeCombo ", e);
                    self.currentScheme = e;
                    filteredGrid.setScheme(e);
                    addConceptButton.setDisabled(false);
                }
                else
                {
                      filteredGrid.ResetConceptGrid();
                      addConceptButton.setDisabled(true);
                }



            });



                  on(addConceptButton, "click", function(){
                console.log("on addConceptButton " + self.currentScheme);
                conceptDialog.content.init(self.currentScheme);
                conceptDialog.show();
            });

           schemeFileteringSelect.startup();

            topic.subscribe("concept.open", lang.hitch(this, function(conceptid, schemeid){
                var cp = registry.byId(schemeid + "_" + conceptid);
                if (cp){
                    tc.selectChild(cp);
                }
                else {
                    var thesaurus = self.thesauri.stores[schemeid];
                    thesaurus.get(conceptid).then(function(item){
                        console.log("treestore item: " + item);
                        console.log("create contentpane");
                        var concept = new ConceptDetail({
                            conceptid : item.id,
                            label: item.label,
                            type: item.type,
                            uri: item.uri,
                            schemeid: schemeid,
                            labels: item.labels,
                            notes: item.notes,
                            narrower: item.narrower,
                            related: item.related,
                            broader: item.broader,
                            members: item.members,
                            member_of: item.member_of
                        });
                        cp = new ContentPane({
                            id: schemeid + "_" + item.id,
                            title: item.label,
                            closable: true,
                            style: "padding: 0",
                            content: concept
                        });
                        tc.addChild(cp);
                        tc.selectChild(cp);
                    });
                }

            }));

            topic.subscribe("concept.delete",function(conceptid, schemeid){
                console.log("concept.delete subscribe: " + conceptid + "(" + schemeid + ")");
                var thesaurus = self.thesauri.stores[schemeid];
                filteredGrid.conceptGrid.store.remove(conceptid)
                    .then(function(){
                        filteredGrid.conceptGrid.refresh();
                        var cp = registry.byId(schemeid + "_" + conceptid);
                        tc.removeChild(cp);
                        cp.destroyRecursive();
                     });
            });

            topic.subscribe("concept.edit",function(conceptid, schemeid){
                console.log("concept.edit subscribe: " + conceptid + "(" + schemeid + ")");
            });

            topic.subscribe("conceptform.submit", function(form){
                console.log("conceptform.submit subscribe");
                console.log(form);

                var rowToAdd = {
                    "type": form.ctype,
                    "narrower": [],
                    "related": [],
                    "labels": [
                        {
                            "type": form.clabeltype,
                            "language": form.clabellang,
                            "label": form.clabel
                        }
                    ],
                    "notes": [],
                    "broader": [
                        form.cbroader
                    ]
                };
                filteredGrid.conceptGrid.store.add(rowToAdd)
                    .then(function(){
                        filteredGrid.conceptGrid.refresh();
                        console.log("row added");
                        conceptDialog.content.show({
                            spinnerNode: false,
                            formNode: false,
                            successNode: true
                        });
                        conceptDialog && conceptDialog.resize();
                    });
                });

            var currentUser=null;
              currentUser=cookie("_USER_");
             var auth_tkt = cookie("auth_tkt");
             var userinfo=new Toggler({node:'user_info'});
             var signout=new Toggler({node:'signout'});
             var signin=new Toggler({node:'signin'});

            if(currentUser!=null)
            {

                if(auth_tkt!=null)
                {
                    cookie("_USER_","-deleted-",{expire:-1})
                    currentUser=null;

                    userinfo.hide();
                    signout.hide();
                    signin.show();

                }
                else
                {
                    userinfo.show();
                    signout.show();
                    signin.hide();

                }

            }
             else
                {
                    userinfo.hide();
                    signout.hide();
                    signin.show();

                }
             var signInButton=dom.byId("signin");
                        on(signInButton,"click",function()
            {
                   navigator.id.request();

            });

            var signOutButton=dom.byId("signout");

            on(signOutButton,"click",function()
            {
                 navigator.id.request();

            });


              navigator.id.watch({
              loggedInUser: currentUser,
              onlogin: function(assertion) {
                // A user has logged in! Here you need to:
                // 1. Send the assertion to your backend for verification and to create a session.
                // 2. Update your UI.

                request.post("../auth/login",{data: assertion,
                // Wait 4 seconds for a response
							timeout: 4000}).then
                (function(data)
                {
                var convertedData=Json.parse(data);
                currentUser = data.email;
                dom.byId("user_id").innerHTML = currentUser;
                var userinfo=new Toggler({node:'user_info'});
                var signout=new Toggler({node:'signout'});
                var signin=new Toggler({node:'signin'});
                userinfo.show();
                signout.show();
                signin.hide();

                },
                function(err)
                {
                    alert("Logout failure: " + err);
                }


                );

              },

              onlogout: function() {
                // A user has logged out! Here you need to:
                // Tear down the user's session by redirecting the user or making a call to your backend.
                // Also, make sure loggedInUser will get set to null on the next page load.
                // (That's a literal JavaScript null. Not false, 0, or undefined. null.)
                request.post( "../auth/logout").then
                (function(data)
                {
                  var userinfo=new Toggler({node:'user_info'});
                  var signout=new Toggler({node:'signout'});
                  var signin=new Toggler({node:'signin'});
                    currentUser = null;
                    userinfo.hide();
                    signout.hide();
                    signin.show();

                },

                function(err)
                {
                    if(currentUser!=null) {
                        alert("Logout failure: " + err);
                    }
                }

                );
              }
            });



        }

    });
});