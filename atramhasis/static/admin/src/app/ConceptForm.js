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
        RelationManager,
        Select, FilteringSelect,
        ValidationTextBox, Validate, NumberTextBox,
        Button,
        domForm,
        Grid, Selection, Keyboard, editor
    ) {
        return declare([
            Form, _WidgetBase, WidgetsInTemplateMixin, _TemplatedMixin, FormMgrMixin,
            FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin
        ], {

            templateString: template,
            widgetsInTemplate: true,
            dialog: null,
            scheme: null,

            constructor:function (options) {
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
                    'scheme': this.scheme
                }, this.broaderContainerNode);
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
                this.schemeNode.innerHTML = "Scheme: " + scheme;
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