define(
    [
        'dojo/_base/declare',
        "dojo/_base/array",
        "dojo/topic", "dojo/on", "dojo/dom-construct", "dojo/query",
        "dojo/store/Memory",
        "dijit/registry",
        'dijit/_WidgetBase', 'dijit/_TemplatedMixin',
        'dijit/form/Form', "dijit/form/CheckBox",
        'dijit/_WidgetsInTemplateMixin',
        'dojox/form/manager/_Mixin', 'dojox/form/manager/_NodeMixin', 'dojox/form/manager/_FormMixin', 'dojox/form/manager/_DisplayMixin',
        "dojo/text!./templates/ConceptForm.html",
         "./form/LabelManager",
        'dijit/form/Select',
        'dijit/form/FilteringSelect',
        'dijit/form/ValidationTextBox', 'dojox/validate', 'dijit/form/NumberTextBox',
        'dijit/form/Button',
        'dojo/dom-form',
        'dojox/layout/TableContainer',
        'dijit/form/TextBox',
        'dijit/form/ComboBox',
        'dijit/form/NumberSpinner',
        'dojo/_base/lang',
        'dgrid/Grid',
        "dijit/form/Select",
        "dojo/data/ObjectStore",
        './EditLabelTemplate',
        'dijit/Dialog',
        "dgrid/Grid", "dgrid/Selection", "dgrid/Keyboard", "dgrid/editor"
    ],
    function (
        declare, arrayUtil,
        topic, on, domConstruct, query,
        Memory,
        registry,

        _WidgetBase,  _TemplatedMixin,
        Form, CheckBox,
        WidgetsInTemplateMixin,
        FormMgrMixin, FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin,
        template,
        LabelManager,
        Select, FilteringSelect,
        ValidationTextBox, Validate, NumberTextBox,
        Button,
        domForm,
        TableContainer,
        TextBox,
        ComboBox,
        NumberSpinner,

        lang,
        Grid,
        Select,
        ObjectStore,
        EditLabelTemplate,
        Dialog,
        Grid, Selection, Keyboard, editor
    ) {
        var myDialog;
        return declare([
            Form, _WidgetBase, WidgetsInTemplateMixin, _TemplatedMixin, FormMgrMixin,
            FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin
        ], {

            templateString: template,
            widgetsInTemplate: true,
            dialog: null,
            scheme: null,
            labelgrid: null,
            labels: [],

            constructor: function (options) {
                declare.safeMixin(this, options);
                this.inherited(arguments)
            },
            postCreate:function () {
                this.inherited(arguments);
                this.labelManager = new LabelManager({
                    'name': 'lblMgr'
                }, this.labelContainerNode);
            },

            startup: function () {
                       this.inherited(arguments);
            },

            onSubmit:function (evt) {
                evt.preventDefault();
                this.inherited(arguments);
                this.validate();
                if (this.isValid()) {
                    var formObj = domForm.toObject(this.containerNode);
                    console.log(formObj);
                    topic.publish("conceptform.submit", formObj);
                }
                this.show({
                    spinnerNode: true,
                    formNode: false,
                    successNode: false
                });
                this.dialog && this.dialog.layout();

                return false;
            },


            showLabelDialog: function () {
                registry.byId("labeldialog").show();
            },
            labelDialogOk: function () {
                var lblDialog = registry.byId("labeldialog");
                var data = lblDialog.get('value');
                if (this._createLabel(data.clabel, data.clabeltype, data.clabellang)) {
                    lblDialog.reset();
                    lblDialog.hide();
                }
            },
            labelDialogCancel: function () {
                var lblDialog = registry.byId("labeldialog");
                lblDialog.reset();
                lblDialog.hide();
            },

            _createLabel: function (label, type, lang) {
                console.log("saving label: " + label);
                var found = arrayUtil.some(this.labels, function (item) {
                    return item.label == label && item.type == type && item.language == lang;
                });
                if (found) {
                    alert('This label already exisits!');
                    return false;
                } else {
                    var newLabel = {"label": label, "type": type, "language": lang};
                    this.labels.push(newLabel);
                    this._createLabelList();
                    return true;
                }

            },

            _createLabelList: function () {
                var labelListNode = this.labelListNode;
                query("li", labelListNode).forEach(domConstruct.destroy);
                arrayUtil.forEach(this.labels, function (label) {
                    domConstruct.create("li", {
                        innerHTML: "<b>" + label.label + "</b> (<em>" + label.language + "</em>): " + label.type
                    }, labelListNode);
                });
            },

            CreateAndShowAddEditLabel: function () {


             var columns = [
                {label:"Name", field:"name"},
                {label:"Language", field:"language"},
                {label:"Type", field:"type"}
                ];
               // var storedata= new Memory({});

               var grid = new Grid({
                   columns: columns
                    }, "gridlabel");

              grid.startup();

              var labelTabForBoxes = new TableContainer({cols: 4, spacing: 10,orientation:"vert"}, "LabelTabForBoxes");
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
                        onClick: lang.hitch(this, function(evt) {

                            console.log("Add label to tabel in add label dialog");

                            var languageSelected=langStoreComboBox.get('value');
                            var labelTypeSelected=labelStoreComboBox.get('value');
                            var labelName=TitleLAbel.get('value');
                             var dataToStore=[
                                        {name:labelName,language:languageSelected,type:labelTypeSelected}
                                        ];


                            grid.renderArray(dataToStore);
                            //grid.store.add(dataToStore);



                            grid.resize();
                        })
                    }
                );

                labelTabForBoxes.addChild(TitleLAbel);
                labelTabForBoxes.addChild(langStoreComboBox);
                labelTabForBoxes.addChild(labelStoreComboBox);
                labelTabForBoxes.addChild(AddLabelButtonTotable);
                labelTabForBoxes.startup();



                 registry.byId("labeldialog").show();
                           grid.resize();
            },

            init: function (scheme) {
                console.log("init cdialog: " + scheme);
                this.reset();
                this.scheme = scheme;
                registry.byId("cscheme").set("value", scheme);
                /*this.schemeNode.innerHTML = "Scheme: " + scheme;*/
                // this.schemeNodeLabel.innerHTML="Scheme: ";
                // this.schemeNode.set("value",scheme);

                var myTable = new TableContainer({cols: 2, spacing: 10}, "myTable");

                var schemebox = new TextBox({title: "Scheme:"});
                schemebox.set('disabled', true);
                schemebox.set('value', scheme);

                var broaderBox = new NumberSpinner({title: "Broader:"});


                var typeStore = new Memory({
                    data: [
                        {name: "concept", id: "concept"},
                        {name: "collection", id: "collection"}
                    ]
                });

                var typeComboBox = new ComboBox({
                    id: "typecombobox",
                    name: "typeComboBox",
                    store: typeStore,
                    searchAttr: "name",
                    title: "Type:"
                });

                typeComboBox.startup();

                var AddLabelButton = new Button
                ({
                        label: "Add label:",
                        iconClass: 'plusIcon',
                        showLabel: false,
                        onClick: lang.hitch(this, function(evt) {

                            console.log("ShowLabel dialog");
                            this.CreateAndShowAddEditLabel();



                        })
                    }
                );

                AddLabelButton.startup();
                // Add the four text boxes to the TableContainer
                myTable.addChild(schemebox);
                myTable.addChild(typeComboBox);
                myTable.addChild(broaderBox);
                myTable.addChild(AddLabelButton);
                myTable.startup();
                this.show({
                    spinnerNode: false,
                    formNode: true,
                    successNode: false
                });
                this.dialog && this.dialog.layout();
            }

        });

    }
);