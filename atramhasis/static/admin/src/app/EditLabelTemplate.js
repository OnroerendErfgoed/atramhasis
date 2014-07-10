define([
    'dijit/_TemplatedMixin',
    'dijit/_WidgetsInTemplateMixin',
    'dojo/_base/declare',
    'dijit/Dialog',
    'dojo/text!./templates/EditLabelTemplate.html',
    'dijit/form/Button'

], function (TemplatedMixin, WidgetsInTemplateMixin, declare, Dialog, template,Button) {
    return declare([Dialog, TemplatedMixin, WidgetsInTemplateMixin], {
        templateString: template,

        postMixInProperties: function () {
            this.inherited(arguments);
        },

        buildRendering: function () {
            this.inherited(arguments);
        },

        postCreate: function () {
            this.inherited(arguments);
        },

        startup: function () {
            this.inherited(arguments);

        },

            init: function ()
            {
                var addLabelButton = new Button({
                label: "Add Label"
            }, "addLabeltNode");
            }


    });
});
