define([
    'dojo/_base/declare',
    'dijit/_WidgetBase',
    'dojo/Evented',
    'dojo/dom-construct',
    'dojo/on',
    'dojo/string',
    'dijit/Dialog',
    'dijit/form/Select',
    'dijit/form/TextBox',
    'dijit/form/Button',
    'dgrid/List',
    'dgrid/Keyboard',
    'dgrid/Selection',
    'dgrid/extensions/DijitRegistry'    
], function (declare, WidgetBase, Evented, domConstruct, on, string, Dialog, Select, TextBox, Button,
    dgridList, dgridKeyboard, dgridSelection, DijitRegistry) {
    return declare([WidgetBase, Evented], {

        externalSchemeService: null,

        _externalConceptList: null,

        _dialog: null,

        _selectedScheme: null,

        postCreate: function () {
            this.inherited(arguments);
        },

        startup: function () {
            this.inherited(arguments);
        },

        showDialog: function () {
            if (this._dialog == null) {
                this._dialog = this._createDialog();
            }
            this._dialog.show();
        },

        _createDialog: function () {
            var self = this;

            var dlg = new Dialog({
                'class': "externalForm",
                'title': "Choose an external concept"
            });

            var searchDiv = domConstruct.create("div", {}, dlg.containerNode);

            domConstruct.create("p", {
                'innerHTML': "Select an external scheme and enter a label to search for a concept:"
            }, searchDiv);
            var selectScheme = new Select({
                name: "extSchemeSelect",
                store: this.externalSchemeService.getExternalSchemeStore(),
                style: "width: 200px;",
                title: "Select external scheme",
                labelAttr: "label",
                maxHeight: -1 // tells _HasDropDown to fit menu within viewport
            }).placeAt(searchDiv);

            var textFilter = new TextBox({
                name: "matchFilter",
                placeHolder: "search for label",
                intermediateChanges: true
            }).placeAt(searchDiv);

            new Button({
                "label": "Search",
                onClick: function(){
                    self.externalSchemeService.searchConcepts(selectScheme.value, textFilter.value).then(
                        function(data){
                            self._selectedScheme = selectScheme.value;
                            self._externalConceptList.refresh();
                            self._externalConceptList.renderArray(data);
                        }, function(err){
                            self._selectedScheme = null;
                            console.error(err);
                        }
                    );
                }
            }).placeAt(searchDiv);

            var listHolder = domConstruct.create("div", {}, searchDiv);
            var list = new (declare([dgridList, dgridKeyboard, dgridSelection, DijitRegistry]))({
                selectionMode: "single",
                renderRow: function(object, options){
                    return domConstruct.create("div", {
                        innerHTML: string.escape(object.label.toString()) + " <em>("
                          + string.escape(object.type.toString()) + ", id: "
                          + string.escape(object.id.toString()) + ")</em>"
                    });
                }
            }, listHolder);
            list.renderArray([]);
            this._externalConceptList = list;

            var actionBar = domConstruct.create("div", {
                'class': "dijitDialogPaneActionBar",
                width: "300px"
            }, dlg.containerNode);


            var previewBtn = new Button({
                "label": "Preview concept"
            }).placeAt(actionBar);

            var addBtn = new Button({
                "label": "Import"
            }).placeAt(actionBar);

            var cancelBtn = new Button({
                "label": "Cancel"
            }).placeAt(actionBar);

          previewBtn.onClick = function () {
                var row = null;
                for(var id in list.selection){
                    if(list.selection[id]){
                        row = list.row(id);
                    }
                }

                if (row && row.data && row.data.uri) {
                    window.open(row.data.uri);
                }
                else {
                    console.info('No concept selected.');
                }
          };

          addBtn.onClick = function () {
                var row = null;
                for(var id in list.selection){
                    if(list.selection[id]){
                        row = list.row(id);
                    }
                }

                if (row) {
                    self.emit('select', {concept: row.data, scheme: self._selectedScheme});
                    dlg.hide();
                }
                else {
                    console.info('No concept selected.');
                }
            };

            cancelBtn.onClick = function () {
                self.emit('cancel', {});
                dlg.hide();
            };

            on(dlg, "hide", function () {
                textFilter.reset();
                list.clearSelection();
            });

            return dlg
        }

    });
});