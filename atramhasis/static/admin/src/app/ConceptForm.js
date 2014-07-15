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
        "./form/RelationManager",
        'dijit/form/Select',
        'dijit/form/FilteringSelect',
        'dijit/form/ValidationTextBox', 'dojox/validate', 'dijit/form/NumberTextBox',
        'dijit/form/Button',
        'dojo/dom-form',
        'dojox/layout/TableContainer',
        'dijit/form/TextBox',
        'dijit/form/ComboBox',

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
        RelationManager,
        Select, FilteringSelect,
        ValidationTextBox, Validate, NumberTextBox,
        Button,
        domForm,
        TableContainer,
        TextBox,
        ComboBox

    ) {
        return declare([
            Form, _WidgetBase, WidgetsInTemplateMixin, _TemplatedMixin, FormMgrMixin,
            FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin
        ], {

            templateString: template,
            widgetsInTemplate: true,
            dialog: null,
            scheme: null,

            constructor: function (options) {
                declare.safeMixin(this, options);
                this.inherited(arguments)
            },
            postCreate:function () {
                this.inherited(arguments);
                this.labelManager = new LabelManager({
                    'name': 'lblMgr'
                }, this.labelContainerNode);
                this.broaderManager = new RelationManager({
                    'name': 'broaderMgr',
                    'title': 'Broader:',
                    'scheme': this.scheme
                }, this.broaderContainerNode);
                this.narrowerManager = new RelationManager({
                    'name': 'narrowerMgr',
                    'title': 'Narrower:',
                    'scheme': this.scheme
                }, this.narrowerContainerNode);
                this.relatedManager = new RelationManager({
                    'name': 'relatedMgr',
                    'title': 'Related:',
                    'scheme': this.scheme
                }, this.relatedContainerNode);
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
                    formObj.broader = this.broaderManager.getRelations();
                    formObj.narrower = this.narrowerManager.getRelations();
                    formObj.related = this.relatedManager.getRelations();
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

            init: function(scheme) {
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
                // Add the four text boxes to the TableContainer
                myTable.addChild(schemebox);
                myTable.addChild(typeComboBox);
                myTable.startup();
                this.broaderManager.scheme = scheme;
                this.narrowerManager.scheme = scheme;
                this.relatedManager.scheme = scheme;
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