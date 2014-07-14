define([
        "dojo/_base/declare",
        "dijit/Dialog",
	    "dijit/_WidgetBase",
	    "dijit/_TemplatedMixin",
        "dijit/form/Form",
        "dijit/form/Button",
        "dijit/form/Select",
        "dgrid/OnDemandGrid",
        "dijit/form/TextBox",
        "dojox/layout/TableContainer",
        "dojo/_base/lang",
        "dojo/dom-construct",
        "dojo/store/Memory",
        "dojo/store/Observable",
        "dgrid/editor",
        "dojo/text!./templates/LabelManager.html"

	 ],
function(
    declare,
    Dialog,
    WidgetBase,
    TemplatedMixin,
    Form, Button,Select,OnDemandGrid,TextBox,TableContainer,lang,domConstruct,Memory,Observable,editor,template
) {
	return declare(
		"app/form/LabelManager",
		[WidgetBase, TemplatedMixin],
	{
        templateString: template,

        name: 'LabelManager',

        buildRendering: function() {
            this.inherited(arguments);
        },

         onSubmit:function (evt) {
                evt.preventDefault();
                this.inherited(arguments);
                this.validate();
                if (this.isValid()) {
                    var formObj = domForm.toObject(this.containerNode);
                    console.log(formObj);

                }
                this.show({
                    spinnerNode: true,
                    formNode: false,
                    successNode: false
                });
                this.dialog && this.dialog.layout();

                return false;
            },


        postCreate: function() {
            this.inherited(arguments);

            var form = new Form();

            this.CreateEditLabelForm(form);

            new Button({
                label: "submit",
                type:'submit'
            }).placeAt(form.containerNode);

            var labelGridDialog = new Dialog({
                content: form,
                title: "Label Manager"


            });



            form.startup();

            var myButton = new Button({
                label: "Manage labels",
                onClick: function(){
                    console.log("click in labelMananger");
                    labelGridDialog.show();
                }
            }, this.labelButton)
        },

           CreateEditLabelForm: function (form) {


             var mainDiv=domConstruct.create("div");

            domConstruct.place(mainDiv,form.containerNode);

            var griddiv=domConstruct.create("div");

             domConstruct.place(griddiv,mainDiv,"last");

             var tableBoxdiv=domConstruct.create("div");
             domConstruct.place(tableBoxdiv,mainDiv,"first");



               var columns = [
                {label:"Title", field:"name"},
                {label:"Language", field:"language"},
                {label:"Type", field:"type"},
                editor({label:" ",field:'button',
                    editorArgs:{label:"delete",onClick:function(event){
                        var row=grid.row(event);
                        var itemToDelete=row.data.id;
                        grid.store.remove(itemToDelete);
                        grid.resize();

                    }
                    }},
                    Button)
                ];

               var dataToStore=[];
               var gridStore=new Memory({
                    data: []

                });

               var observableStore=new Observable(gridStore);

               var grid = new OnDemandGrid({
                   columns: columns,
                   store:observableStore,
                 selectionMode: "single", // for Selection; only select a single row at a time
                    cellNavigation: false // for Keyboard; allow only row-level keyboard navigation

                    },griddiv);

              grid.startup();
              var row;
               grid.on(".dgrid-row:click", function(event){
                    row = grid.row(event);

                    });

              var labelTabForBoxes = new TableContainer({cols: 4, spacing: 10,orientation:"vert"},tableBoxdiv);
                var TitleLAbel = new TextBox({title: "Title:"});

                  var labelStoreComboBox = new Select(
                      {
                        id: "labelStoreComboBox",
                        name: "labelStoreComboBox",
                        title: "Type of label:",
                        options:[
                            {label:"Preferred",value:"Preferred"},
                            {label:"Alternative",value:"Alternative"},
                            {label:"Hidden",value:"Hidden"}
                        ],
                       style:{ width: '100px' }
                  });

                 var langStoreComboBox = new Select({

                    id: "langStoreComboBox",
                    name: "langStoreComboBox",
                    title: "Language:",
                    options:[

                            {label:"Nl",value:"NL"},
                            {label:"Fr",value:"Fr"},
                            {label:"En",value:"En"}

                        ],
                     style:{ width: '80px' }
                 });

               var AddLabelButtonTotable = new Button
               ({
                       iconClass: 'plusIcon',
                       showLabel: false,
                       onClick: lang.hitch(this, function (evt) {

                           console.log("Add label to tabel in add label dialog");

                           var languageSelected = langStoreComboBox.get('value');
                           var labelTypeSelected = labelStoreComboBox.get('value');
                           var labelName = TitleLAbel.get('value');
                           var tempDataToStore = [
                               {name: labelName, language: languageSelected, type: labelTypeSelected}
                           ];

                           //dataToStore[dataToStore.length]=tempDataToStore;
                           //grid.renderArray(tempDataToStore);

                          //gridStore.add(tempDataToStore);
                          grid.store.add( {name: labelName, language: languageSelected, type: labelTypeSelected});

                           grid.resize();
                       })
                   }
               );

                labelTabForBoxes.addChild(TitleLAbel);
                labelTabForBoxes.addChild(langStoreComboBox);
                labelTabForBoxes.addChild(labelStoreComboBox);
                labelTabForBoxes.addChild(AddLabelButtonTotable);
                labelTabForBoxes.startup();
                grid.resize();
            }




	});
});
