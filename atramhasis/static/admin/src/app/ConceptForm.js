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
            dialog: null,
            scheme: null,
            labelgrid: null,
            labels: [],

            constructor:function (options) {
                declare.safeMixin(this, options);
                this.inherited(arguments)
            },
            postCreate:function () {
                this.inherited(arguments);
//                this.hide(['urlField']);
            },

            startup: function () {
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

            testt: function() {
              alert('ok');
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