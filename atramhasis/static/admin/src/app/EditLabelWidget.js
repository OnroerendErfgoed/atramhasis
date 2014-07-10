define(
    [
        'dojo/_base/declare',
        'dijit/form/Form', 'dijit/_WidgetsInTemplateMixin',
        'dojox/form/manager/_Mixin', 'dojox/form/manager/_NodeMixin', 'dojox/form/manager/_FormMixin', 'dojox/form/manager/_DisplayMixin',
        'dijit/form/ValidationTextBox', 'dojox/validate',
        'dijit/form/Button',
        'dojo/text!./templates/EditLabelTemplate.html'
    ],
    function (
        declare,
        Form, WidgetsInTemplateMixin,
        FormMgrMixin, FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin,
        ValidationTextBox, Validate,
        Button,template
    ) {
        return declare([Form, WidgetsInTemplateMixin, FormMgrMixin, FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin], {
            templateString:template,
            resources:null,
            dialog:null,
            constructor:function (options) {
                declare.safeMixin(this, options);
                this.inherited(arguments)
            },
            postCreate:function () {
                this.inherited(arguments);
                this.hide(['urlField']);
            },
            reactor:function (value, field) {
                if ('name' == field && 0 < value.length) {
                    this.show(['urlField']);
                } else {
                    this.hide(['urlField']);
                }
                this.dialog && this.dialog.resize();
            },
            onSubmit:function () {
                this.inherited(arguments);
                this.validate();
                if (this.isValid()) {
                    alert(this.resources.submitYourForm);
                }
                return false;
            }

             startup: function () {
                       this.inherited(arguments);
            },

        });
    }
);