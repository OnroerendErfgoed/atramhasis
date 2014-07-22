define([
    "dojo/_base/declare",
    "dojo/on",
    "dojo/topic",
    "dojo/_base/lang",

    "dijit/_Widget",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "dojo/text!./templates/FilteredGrid.html",

    "dijit/form/ComboBox",
    "dijit/form/TextBox",
    "dijit/form/Button",
    "dijit/Menu",
    "dijit/MenuItem",
    "dojo/store/Memory", "dojo/store/Cache",
    "dgrid/OnDemandGrid", "dgrid/Selection", "dgrid/Keyboard", "dgrid/editor"

], function (declare, on, topic, lang, _Widget, _TemplatedMixin, _WidgetsInTemplateMixin, template, ComboBox, TextBox, Button, Menu, MenuItem, Memory, Cache, OnDemandGrid, Selection, Keyboard, editor) {
    return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {
        templateString: template,

        concepttypes: null,
        conceptStore: null,
        conceptScheme: null,

        typeCombo: null,
        textFilter: null,
        conceptGrid: null,
        conceptFilter: {label: "", type: "all"},
        isResettingFilters: true,

        postMixInProperties: function () {
            this.inherited(arguments);
        },

        buildRendering: function () {
            this.inherited(arguments);
        },

        postCreate: function () {
            this.inherited(arguments);

            this.concepttypes = new Memory({
                data: [
                    {name: "All", id: "all"},
                    {name: "Concepts", id: "concept"},
                    {name: "Collections", id: "collection"}
                ]});
        },

        startup: function () {
            this.inherited(arguments);
            var self = this;
            console.log("startup grid");

            var timeoutId;

            this.typeCombo = new ComboBox({
                id: "typeSelect",
                name: "ctype",
                store: this.concepttypes,
                searchAttr: "id",
                placeHolder: 'filter by type'
            }, "typeNode");

            this.textFilter = new TextBox({
                id: "labelFilter",
                name: "labelFilter",
                placeHolder: 'filter by label',
                intermediateChanges: true
            }, "filterNode");

            var self = this;

            var columns = [
                {label: "ID", field: "id"},
                {label: "label", field: "label"},
                {label: "Type", field: "type"},
                {label: "URI", field: "uri"}

            ];

            this.conceptGrid = new (declare([OnDemandGrid, Selection, Keyboard]))({
                sort: "id",
                columns: columns,
                selectionMode: "single",
                minRowsPerPage: 20,
                maxRowsPerPage: 100

            }, "gridNode");

            on(this.conceptGrid, "dgrid-select", lang.hitch(this, function (evt) {
                var row = evt.rows[0];
                row.scheme = this.conceptScheme;
                console.log("row selected: " + row.id);
                topic.publish("concept.open", row.id, row.scheme);
            }));

            this.conceptGrid.on(".dgrid-row:contextmenu", function (evt) {
                    evt.preventDefault();


                    var cell = self.conceptGrid.cell(evt);
                    var gridId = self.conceptGrid.get("id");
                    var pMenu = self._createGridContextMenu(gridId, cell.element, self);
                    var args = {target: pMenu.selector};
                    pMenu._openMyself(args);

                }
            );


            on(this.typeCombo, "change", lang.hitch(this, function (evt) {
                if (evt != "") {
                    console.log("on ", evt);
                    this._setTypeFilter(evt);
                }

            }));

            this.textFilter.watch("value", (lang.hitch(this, function (name, oldValue, newValue) {
                if (this.isResettingFilters) return false;
                console.log("typing text: " + newValue);
                if (timeoutId) {
                    clearTimeout(timeoutId);
                    timeoutId = null;
                }
                timeoutId = setTimeout(lang.hitch(this, function () {
                    this._setTextFilter(newValue);
                }, 300));
                return true;
            })));
        },

        _resetFilters: function () {
            console.log("grid _reset");
            this.isResettingFilters = true;
            this.typeCombo.reset();
            this.textFilter.reset();
            this.conceptFilter = {label: "", type: "all"};
            this.isResettingFilters = false;
        },

        setScheme: function (schemeid) {
            console.log("grid setScheme: " + schemeid);
            this._resetFilters();
            this.conceptScheme = schemeid;
            this.conceptStore = Cache(dojo.store.JsonRest({
                target: "/conceptschemes/" + schemeid + "/c",
                sortParam: "sort"
            }), Memory());
            this.conceptGrid.set("store", this.conceptStore, this.conceptFilter);
        },

        ResetConceptGrid: function () {
            this._resetFilters();

            this.conceptStore = null;
            this.conceptGrid.set("store", this.conceptStore, this.conceptFilter);

        },


        _setTypeFilter: function (type) {
            console.log("setting type filter: " + type);
            this.conceptFilter = {label: this.conceptFilter.label, type: type};
            this.conceptGrid.set("query", this.conceptFilter);
        },

        _setTextFilter: function (label) {
            console.log("setting label filter: " + label);
            this.conceptFilter = {label: label, type: this.conceptFilter.type};
            this.conceptGrid.set("query", this.conceptFilter);
        },

        _createGridContextMenu: function (targetNodeId, selector, widget) {
            var pMenu;
            var self = this;
            pMenu = new Menu({
                targetNodeIds: [targetNodeId],
                selector: selector
            });
            pMenu.addChild(new MenuItem({
                label: "Add narrower",
                onClick: function () {
                    widget._addNarrower();
                }
            }));

            pMenu.addChild(new MenuItem({
                label: "Edit",
                onClick: function () {
                    widget._editConcept();
                }
            }));
            pMenu.addChild(new MenuItem({
                label: "Add a new Concept or collection",
                onClick: function () {
                    widget._createNewConcept();
                }
            }));
            pMenu.addChild(new MenuItem({
                label: "Delete",
                onClick: function () {
                    widget._deleteConcept();
                }
            }));


            pMenu.startup();
            return pMenu;
            var args = {target: pMenu.selector};
            pMenu._openMyself(args);


        },


        _addNarrower: function () {

            alert('i was clicked');

        },

        _editConcept: function () {
            alert('i was clicked');

        },

        _createNewConcept: function () {

            alert('i was clicked');
        },

        _deleteConcept: function () {

            alert('i was clicked');

        }



    });

});
