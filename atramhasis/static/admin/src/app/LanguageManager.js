define([
    'dijit/_WidgetBase',
    'dojo/_base/declare',
    'dojo/_base/lang',
    'dojo/dom-construct',
    'dojo/on',
    'dojo/when',
    'dojo/Evented',
    'dojo/store/JsonRest',
    'dojo/store/Observable',
    'dijit/Dialog',
    'dijit/form/Button',
    'dijit/form/TextBox',
    'dgrid/OnDemandGrid',
    'dgrid/Keyboard',
    'dgrid/Selection',
    'dgrid/extensions/DijitRegistry',
    "dgrid/editor"
], function (
    WidgetBase,
    declare,
    lang,
    domConstruct,
    on,
    when,
    Evented,
    JsonRest,
    Observable,
    Dialog,
    Button,
    TextBox,
    OnDemandGrid,
    dgridKeyboard,
    dgridSelection,
    DijitRegistry,
    editor
    ) {
    return declare([WidgetBase, Evented], {

        languageStore: null,

        _languageDialog: null,

        _languageName: null,

        _languageCode: null,

        _languageGrid: null,

        postCreate: function () {
            this.inherited(arguments);
            //todo eventueel listcontroller aanmaken stores cachen
            var masterStore = new JsonRest({
                'target': '/languages',
                'idProperty': 'id',
                'sortParam': 'sort',
                'accepts': 'application/json'
            });
            this.languageStore = new Observable(masterStore);
        },

        startup: function () {
            this.inherited(arguments);
        },

        showDialog: function () {
            if (this._languageDialog == null) {
                this._languageDialog = this._createDialog();
            }
            this._languageDialog.show();
        },

        _createDialog: function () {

            var dlg = new Dialog({
                'class': "externalForm",
                'title': "Manage languages",
                'style': "width: 500px"
            });

            var addGridContainer = domConstruct.create("fieldset", {}, dlg.containerNode);

            domConstruct.create("legend", {
                innerHTML: "Add a language:"
            }, addGridContainer);

            var langCode = new TextBox({
                name: "langCode",
                placeHolder: "code"
            }).placeAt(addGridContainer);
            this._languageCode = langCode;

            var langName = new TextBox({
                name: "langName",
                placeHolder: "name"
            }).placeAt(addGridContainer);
            this._languageName = langName;

            var addBtn = new Button({
                "label": "Add"
            }).placeAt(addGridContainer);

            addBtn.onClick = lang.hitch(this, function () {
                var name = langName.get("value");
                var code = langCode.get("value");
                if (name.trim().length > 0 && code.trim().length) {
                    this._addLanguage(name, code);
                }
                this.reset();
            });

            domConstruct.create("div", {
                innerHTML: "<p>You can use <a href='http://www.iana.org/assignments/language-subtag-registry/language-subtag-registry' target='_blank'>this</a> list as a reference.</p>"
            }, dlg.containerNode);

            var gridDiv = domConstruct.create("div", {}, dlg.containerNode);
            var grid = this._createLangGrid(gridDiv);
            this._languageGrid = grid;

            var actionBar = domConstruct.create("div", {
                'class': "dijitDialogPaneActionBar"
            }, dlg.containerNode);

            var deleteBtn = new Button({
                "label": "Delete language"
            }).placeAt(actionBar);

            deleteBtn.onClick = lang.hitch(this, function () {
                for(var id in grid.selection){
                    if(grid.selection[id]){
                        if (confirm("Are you sure you want to delete '" + id + "'?")) {
                            this._deleteLanguage(id);
                        }
                    }
                }
            });

            new Button({
                label: "Close",
                onClick: function () {
                    dlg.hide();
                }
            }).placeAt(actionBar);

            on(dlg, "hide", lang.hitch(this, function () {
                this.reset();
            }));

            return dlg;
        },

        _createLangGrid: function (node) {
            return new (declare([OnDemandGrid, dgridKeyboard, dgridSelection, DijitRegistry]))({
                sort: "id",
                columns: [
                    {label:'Id', field:'id', sortable: true},
                    editor({
                        field: "name",
                        label: "Name",
                        editor: TextBox,
                        autoSave: true,
                        editOn: "dgrid-cellfocusin",
                        sortable: true
                    })
                ],
                store: this.languageStore,
                selectionMode: "single"
            }, node);
        },

        _addLanguage: function (name, id) {
            var self = this;
            when(this.languageStore.add({name : name, id : id})).then(
                function (lang) {
                    var message = 'New language added: ' + lang.name;
                    self._handleChange(message);
                },
                function (error) {
                    self._handleError(error);
                }
            );
        },

        _deleteLanguage: function (id) {
            var self = this;
            when(this.languageStore.remove(id)).then(
                function () {
                    var message = 'Language removed: ' + id;
                    self._handleChange(message);
                },
                function (error) {
                    self._handleError(error);
                }
            );
        },

        _handleError: function (error) {
            this.emit('error', {
                'title':'bieeep...',
                'message': error.message
            });
        },

        _handleChange: function (message) {
            this.emit('change', {
                'title': 'Languages',
                'message': message
            });
        },

        reset: function () {
            this._languageName.reset();
            this._languageCode.reset();
            this._languageGrid.clearSelection();
        }
    });
});
