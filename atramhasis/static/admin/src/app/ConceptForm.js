define(
    [
        'dojo/_base/declare',
        "dojo/topic",
        'dijit/form/Form', 'dijit/_WidgetsInTemplateMixin',
        'dojox/form/manager/_Mixin', 'dojox/form/manager/_NodeMixin', 'dojox/form/manager/_FormMixin', 'dojox/form/manager/_DisplayMixin',
        'dijit/form/Select',
        'dijit/form/ValidationTextBox', 'dojox/validate', 'dijit/form/NumberTextBox',
        'dijit/form/Button',
        'dojo/dom-form'
    ],
    function (
        declare,
        topic,
        Form, WidgetsInTemplateMixin,
        FormMgrMixin, FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin,
        Select,
        ValidationTextBox, Validate, NumberTextBox,
        Button,
        domForm
    ) {
        return declare([Form, WidgetsInTemplateMixin, FormMgrMixin, FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin], {
            templateString:null,
            dialog:null,
            constructor:function (options) {
                declare.safeMixin(this, options);
                this.inherited(arguments)
            },
            postCreate:function () {
                this.inherited(arguments);
//                this.hide(['urlField']);
            },
//            reactor:function (value, field) {
//                if ('name' == field && 0 < value.length) {
//                    this.show(['urlField']);
//                } else {
//                    this.hide(['urlField']);
//                }
//                this.dialog && this.dialog.resize();
//            },
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

            init: function() {
                this.reset();
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