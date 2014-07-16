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
        "dojo/query",
        "dgrid/extensions/ColumnHider",
         "dojo/_base/array",
        "dojo/text!./templates/LabelManager.html"

	 ],
function(
    declare,
    Dialog,
    WidgetBase,
    TemplatedMixin,
    Form, Button,Select,OnDemandGrid,TextBox,TableContainer,lang,domConstruct,Memory,Observable,editor,query,ColumnHider
    ,arrayUtil,template
) {
	return declare(
		"app/form/LabelManager",
		[WidgetBase, TemplatedMixin],
	{
        templateString: template,

        name: 'LabelManager',
        grid:null,
        TitleLAbel:null,
        LabelGridContent:null,
        langStoreComboBox:null,
        labelStoreComboBox:null,

        buildRendering: function() {
            this.inherited(arguments);
        },
        postCreate: function() {
            this.inherited(arguments);

            var form = new Form();
            var self = this;
            form.onSubmit = function(evt){

                evt.preventDefault();
                LabelGridContent = grid.store.data;
                self._createLabelList(grid.store.data);
                labelGridDialog.hide();
            }

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
                {label:"Title", field:"label"},
                {label:"Language", field:"language"},
                {label:"Language", field:"languageValue",unhidable: true,hidden: true},
                {label:"Type", field:"type"},
                {label:"Type", field:"typeValue",unhidable: true,hidden: true},
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

                grid = new (declare([OnDemandGrid, ColumnHider]))({
                   columns: columns,
                   store:observableStore,
                 selectionMode: "single" // for Selection; only select a single row at a time
                    },griddiv);

              grid.startup();
              var row;
               grid.on(".dgrid-row:click", function(event){
                    row = grid.row(event);

                    });

              var labelTabForBoxes = new TableContainer({cols: 4, spacing: 10,orientation:"vert"},tableBoxdiv);
                TitleLAbel = new TextBox({id:"TitleLAbel",title: "Title:"});

                   labelStoreComboBox = new Select(
                      {
                        id: "labelStoreComboBox",
                        name: "labelStoreComboBox",
                        title: "Type of label:",
                        placeHolder: 'Select a type',
                        options:[
                            {label:"Preferred",value:"prefLabel"},
                            {label:"Alternative",value:"altLabel"},
                            {label:"Hidden",value:"hiddenLabel"}
                        ]
                  });

                  langStoreComboBox = new Select({

                    id: "langStoreComboBox",
                    name: "langStoreComboBox",
                    title: "Language:",
                    placeHolder: 'Select a language',
                    options:[

                            {label:"NL",value:"nl"},
                            {label:"Fr",value:"fr"},
                            {label:"En",value:"en"}

                        ],
                     style:{ width: '80px' }

                 });

               var AddLabelButtonTotable = new Button
               ({
                       iconClass: 'plusIcon',
                       showLabel: false,
                       onClick: lang.hitch(this, function (evt) {

                           console.log("Add label to tabel in add label dialog");

                           var languageSelected = langStoreComboBox.get('displayedValue');
                           var labelTypeSelected = labelStoreComboBox.get('displayedValue');
                           var labelName = TitleLAbel.get('value');

                          grid.store.add(  {label: labelName, language: languageSelected,languageValue:langStoreComboBox.get('value'),

                                   type: labelTypeSelected,typeValue:labelStoreComboBox.get('value')});

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
            },

            _createLabelList: function(labels) {
                var labelListNode = this.labelListNode;
                query("li", labelListNode).forEach(domConstruct.destroy);
                arrayUtil.forEach(labels, function(label){
                    domConstruct.create("li", {
                        innerHTML: "<b>" + label.name + "</b> (<em>" + label.language + "</em>): " + label.type
                    }, labelListNode);
                });
            },

           
            getLabels:function()
            {

                var labels=grid.store.data;

                var labelsToSend=[];
                 arrayUtil.forEach(labels, function(label){

                    var labelToSend=                        {
                            "type":  label.typeValue,
                            "language": label.languageValue,
                            "label": label.label
                        }

                    labelsToSend.push(labelToSend);
                });


                return labelsToSend;
            },


            reset:function()
            {

               var dataToStore=[];
               var gridStore=new Memory({
                    data: []

                });
               TitleLAbel.set("value","");
               langStoreComboBox.reset();
               labelStoreComboBox.reset();
               var observableStore=new Observable(gridStore);
                grid.set("store",observableStore);
                var labelListNode = this.labelListNode;
                query("li", labelListNode).forEach(domConstruct.destroy);

            }



	});
});
