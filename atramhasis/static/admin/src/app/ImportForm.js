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
        "dojo/text!./templates/ImportForm.html",
        'dijit/form/Select',
        'dijit/form/FilteringSelect',
        'dijit/form/ValidationTextBox', 'dojox/validate', 'dijit/form/NumberTextBox',
        'dijit/form/Button',
        'dojo/dom-form',
        'dojox/layout/TableContainer',
        'dijit/form/TextBox',
        'dijit/form/ComboBox',
        "dojo/_base/lang",
        "./ImportGrid",
    ],
    function (declare, arrayUtil, topic, on, domConstruct, query, Memory, registry, _WidgetBase, _TemplatedMixin, Form, CheckBox, WidgetsInTemplateMixin, FormMgrMixin, FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin, template, Select, FilteringSelect, ValidationTextBox, Validate, NumberTextBox, Button, domForm, TableContainer, TextBox, ComboBox, lang, ImportGrid) {
        return declare([
                Form, _WidgetBase, WidgetsInTemplateMixin, _TemplatedMixin, FormMgrMixin,
                FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin
            ], {
                templateString: template,
                widgetsInTemplate: true,
                dialog: null,
                scheme: null,
                schemebox: null,
                conceptId: null,
                externalSchemelist: [],
                importGrid: null,

                constructor: function (options) {
                    declare.safeMixin(this, options);
                    this.inherited(arguments);
                    this.externalSchemelist = options.externalSchemelist;
                },
                postCreate: function () {
                    this.inherited(arguments);

                    var myTable = new TableContainer({cols: 2, spacing: 10}, this.MyTable);
                    schemebox = new ComboBox({
                        id: "importschemecombobox",
                        name: "importschemecombobox",
                        store: new Memory({ data: this.externalSchemelist }),
                        searchAttr: "id",
                        title: "select thesaurus:",
                    });

                    on(schemebox, "change", lang.hitch(this, function (e) {
                        console.log("on schemebox ", e);
                        self.currentScheme = e;
                        this.importGrid.setScheme(e);
                    }));

                    schemebox.startup();

                    // Add the text boxes to the TableContainer
                    myTable.addChild(schemebox);
                    myTable.startup();

                    this.importGrid = new ImportGrid({
                        id: "importGrid"
                    }, "importFilteredGridNode");
                    this.importGrid.startup();

                    var self = this;

                    on(this, "reset", function () {
                        self._resetWidgets();
                        self.conceptId = null;
                    });
                },
                startup: function () {
                    this.inherited(arguments);
                },
                onSubmit: function (evt) {
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
                onCancel: function () {
                    //hide implemented on dialog level
                },
                _resetWidgets: function () {

                },

                init: function () {
                    console.log("init cdialog");
                    this.reset();
                    this.show({
                        formNode: true
                    });
                    this.dialog && this.dialog.layout();
                },
            }
        )
    }
);
