define([
        "dojo/_base/declare",
        "dijit/Dialog",
	    "dijit/_WidgetBase",
	    "dijit/_TemplatedMixin",
        "dijit/form/Form",
        "dijit/form/Button",
        "dojo/text!./templates/LabelManager.html"
	 ],
function(
    declare,
    Dialog,
    WidgetBase,
    TemplatedMixin,
    Form, Button,
    template
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

        postCreate: function() {
            this.inherited(arguments);

            var form = new Form();

            new Button({
                label: "test",
                onClick: function(){
                    console.log("click in labelGridDialog");
                }
            }).placeAt(form.containerNode);

            var labelGridDialog = new Dialog({
                content: form,
                title: "Label Manager",
                style: "width: 300px; height: 300px;"
            });
            form.startup();

            var myButton = new Button({
                label: "Manage labels",
                onClick: function(){
                    console.log("click in labelMananger");
                    labelGridDialog.show();
                }
            }, this.labelButton)
        }
	});
});
