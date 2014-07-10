define([
        "dojo/_base/declare",
        "dojo/_base/array",
        "dojo/dom-construct",
        "dijit/Dialog",
	    "dijit/_WidgetBase",
	    "dijit/_TemplatedMixin",
        "dojo/ready",
        "dojo/parser",
        "dijit/form/Form", 'dijit/form/Button',
        "dojo/store/Memory",
        "dojo/text!./templates/LabelManager.html"
	 ],
function(
    declare, arrayUtil, domConstruct,
    Dialog,
    WidgetBase,
    TemplatedMixin,
    ready,
    parser,
    Form, Button,
    Memory,
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

               var labelStore = new Memory({
                    data: [
                        {name:"Preferred", id:"prefLabel"},
                        {name:"Alternative", id:"altLabel"},
                        {name:"Hidden", id:"hiddenLabel"}
                ]});

               var langStore = new Memory({
                    data: [
                        {name:"Nl", id:"nl"},
                        {name:"Fr", id:"fr"},
                        {name:"En", id:"en"}
                    ]
                });

            var form = new Form();

                new Button({
                  label: "test",
                    onClick: function(){
                        console.log("click 2");
                        dia.show();
                    }
                }).placeAt(form.containerNode);
                //jonathan werk here
                var dia = new Dialog({
                    content: form,
                    title: "Label Manager",
                    style: "width: 300px; height: 300px;"
                });
                form.startup();

             var myButton = new Button({
                    label: "Manage labels",
                    onClick: function(){
                        console.log("click");
                        dia.show();
                    }
                }, this.labelButton)
        },

        _createLabelList: function() {
                var labelListNode = this.labelListNode;
                query("li", labelListNode).forEach(domConstruct.destroy);
                arrayUtil.forEach(this.labels, function(label){
                    domConstruct.create("li", {
                        innerHTML: "<b>" + label.label + "</b> (<em>" + label.language + "</em>): " + label.type
                    }, labelListNode);
                });
        },

        showLabelDialog: function() {
            registry.byId("labeldialog").show();
        },
        labelDialogOk: function() {
            var lblDialog = registry.byId("labeldialog");
            var data = lblDialog.get('value');
            if (this._createLabel(data.clabel, data.clabeltype, data.clabellang)) {
                lblDialog.reset();
                lblDialog.hide();
            }
        },
        labelDialogCancel: function() {
            var lblDialog = registry.byId("labeldialog");
            lblDialog.reset();
            lblDialog.hide();
        },

        _createLabel: function(label, type, lang) {
            console.log("saving label: " + label);
            var found = arrayUtil.some(this.labels, function(item){
                return item.label == label && item.type==type && item.language==lang;
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

        }


	});
});
