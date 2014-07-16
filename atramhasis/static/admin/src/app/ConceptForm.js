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
        'dijit/form/ComboBox'
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
                this.membersManager = new RelationManager({
                    'name': 'membersMgr',
                    'title': 'Members:',
                    'scheme': this.scheme,
                    'style': 'display: none'
                }, this.membersContainerNode);
                this.memberofManager = new RelationManager({
                    'name': 'memberofMgr',
                    'title': 'Member of:',
                    'scheme': this.scheme
                }, this.memberofContainerNode);
                var myTable = new TableContainer({cols: 2, spacing: 10},this.MyTable);
                var schemebox = new TextBox({id:"schemebox",title: "Scheme:"});
                schemebox.set('disabled', true);
                 var typeStore = new Memory({
                    data: [
                        {name: "concept", id: "concept"},
                        {name: "collection", id: "collection"}
                    ]
                });

                var typeComboBox = new ComboBox({
                    id: "typecombobox",
                    name: "ctype",
                    store: typeStore,
                    searchAttr: "name",
                    title: "Type:",
                    value: "concept"
                });
                var self = this;
                typeComboBox.on("change", function(){
                    var val = this.get('value');
                    if (val == 'collection'){
                        self.broaderManager.close();
                        self.narrowerManager.close();
                        self.relatedManager.close();
                        self.membersManager.open();
                        self.memberofManager.open();
                    }
                    else if (val == 'concept'){
                        self.broaderManager.open();
                        self.narrowerManager.open();
                        self.relatedManager.open();
                        self.membersManager.close();
                        self.memberofManager.open();
                    }
                });

                typeComboBox.startup();
                // Add the 3 text boxes to the TableContainer
                myTable.addChild(schemebox);
                myTable.addChild(typeComboBox);
                myTable.startup();

                on(this, "reset", function(){
                    self._resetWidgets();
                });
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
                    formObj.members = this.membersManager.getRelations();
                    formObj.memberof = this.memberofManager.getRelations();
                    formObj.label=this.labelManager.getLabels();
                    console.log(formObj);
                    topic.publish("conceptform.submit", formObj);
                }
                  this.labelManager.reset();

                this.show({
                    spinnerNode: true,
                    formNode: false,
                    successNode: false
                });
                this.dialog && this.dialog.layout();

                return false;
            },

            onCancel: function(){
                //hide implemented on dialog level
            },

            _resetWidgets: function(){
                this.broaderManager.reset();
                this.narrowerManager.reset();
                this.relatedManager.reset();
                this.membersManager.reset();
                this.memberofManager.reset();
                this.labelManager.reset();
            },

            init: function(scheme) {
                console.log("init cdialog: " + scheme);

                this.reset();
                this.scheme = scheme;
                //registry.byId("cscheme").set("value", scheme);
                /*this.schemeNode.innerHTML = "Scheme: " + scheme;*/
                // this.schemeNodeLabel.innerHTML="Scheme: ";
                // this.schemeNode.set("value",scheme);

                var schemebox=dijit.byId("schemebox");
                schemebox.set('value', scheme);

                this.broaderManager.setScheme(scheme);
                this.narrowerManager.setScheme(scheme);
                this.relatedManager.setScheme(scheme);
                this.membersManager.setScheme(scheme);
                this.memberofManager.setScheme(scheme);
                this.show({
                    spinnerNode: false,
                    formNode: true,
                    successNode: false
                });
                this.dialog && this.dialog.layout();
            }
        }
    )}
);