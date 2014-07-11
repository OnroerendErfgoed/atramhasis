define([
        "dojo/_base/declare",
        "dijit/Dialog",
	    "dijit/_WidgetBase",
	    "dijit/_TemplatedMixin",
        "dijit/form/Form",
        "dijit/form/Button",
        "dojo/text!./templates/RelationManager.html"
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
		"app/form/RelationManager",
		[WidgetBase, TemplatedMixin],
	{
        templateString: template,

        name: 'RelationManager',

        buildRendering: function() {
            this.inherited(arguments);
        },

        postCreate: function() {
            this.inherited(arguments);

            var form = new Form();

            new Button({
                label: "test",
                onClick: function(){
                    console.log("click in relationGridDialog");
                }
            }).placeAt(form.containerNode);

            var relationGridDialog = new Dialog({
                content: form,
                title: "Relation Manager",
                style: "width: 300px; height: 300px;"
            });
            form.startup();

            var myButton = new Button({
                label: "Manage relations",
                onClick: function(){
                    console.log("click in relationMananger");
                    relationGridDialog.show();
                }
            }, this.relationButton)
        },

        getRelations: function(){
            var relations = [];
//            relations.push(1);
//            relations.push(4);
            return relations;
        }
	});
});
