define([
    "dojo/_base/declare",
    "dojo/on",
    "dojo/topic",
    "dojo/_base/lang",

    "dijit/_Widget",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "dojo/text!./templates/ImportGrid.html",

    "dijit/form/ComboBox",
    "dijit/form/TextBox",
    "dijit/form/Button",
    "dijit/Menu",
    "dijit/MenuItem",
    "dijit/ConfirmDialog",
    "dojo/store/Memory", "dojo/store/Cache",
    "dgrid/OnDemandGrid", "dgrid/Selection", "dgrid/Keyboard", "dgrid/editor"

], function (declare, on, topic, lang, _Widget, _TemplatedMixin, _WidgetsInTemplateMixin, template, ComboBox, TextBox, Button, Menu, MenuItem, ConfirmDialog, Memory, Cache, OnDemandGrid, Selection, Keyboard, editor) {
    return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {
        templateString: template,

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
        },

        startup: function () {
            this.inherited(arguments);
            var self = this;
            console.log("startup import grid");

            var timeoutId;

            this.textFilter = new TextBox({
                id: "importLabelFilter",
                name: "importLabelFilter",
                placeHolder: 'filter by label',
                intermediateChanges: true
            }, "importFilterNode");

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

            }, "importGridNode");

            on(this.conceptGrid, "dgrid-select", lang.hitch(this, function (evt) {
                var row = evt.rows[0];
                row.scheme = this.conceptScheme;
                console.log("row selected: " + row.id);
                //topic.publish("concept.open", row.id, row.scheme);
            }));

            this.conceptGrid.on(".dgrid-row:contextmenu", function (evt) {
                    evt.preventDefault();

                    var cell = self.conceptGrid.cell(evt);
                    var gridId = self.conceptGrid.get("id");

                }
            );



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
            this.textFilter.reset();
            this.conceptFilter = {label: ""};
            this.isResettingFilters = false;
        },

        setScheme: function (schemeid) {
            console.log("importgrid setScheme: " + schemeid);
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

        _setTextFilter: function (label) {
            console.log("setting label filter: " + label);
            this.conceptFilter = {label: label, type: this.conceptFilter.type};
            this.conceptGrid.set("query", this.conceptFilter);
        }



    });

});
