define([
        "dojo/_base/declare",
        "dojo/_base/array",
        "dojo/dom-construct",
        "dojo/query",
        "dojo/on",
        "dojo/dom-style",
        "dojo/request/xhr",
        "dijit/Dialog",
        "dijit/_WidgetBase",
        "dijit/_TemplatedMixin",
        "dijit/form/Button",
        "dijit/form/Select",
        "dijit/form/TextBox",
        "dojo/store/Memory",
        "dojo/store/Cache",
        "dojo/store/JsonRest",
        "dijit/tree/ObjectStoreModel",
        "dijit/Tree",
        "dojo/topic",
         "./ConceptDetailList",
        "dojo/text!./templates/MatchesManager.html",
        "dgrid/List",
        "dgrid/Keyboard",
        "dgrid/Selection",
         "dgrid/extensions/DijitRegistry"
    ],
    function (declare, arrayUtil, domConstruct, query, on, domStyle, xhr, Dialog, WidgetBase, TemplatedMixin,
              Button, Select, TextBox, Memory, Cache, JsonRest, ObjectStoreModel, Tree,topic,ConceptDetailList, template,
              dgridList, dgridKeyboard, dgridSelection, DijitRegistry) {
        return declare(
            "app/form/RelationManager",
            [WidgetBase, TemplatedMixin],
            {
                templateString: template,
                name: 'MatchesManager',
                title: 'Matches:',
                thesauri: null,
                _matches: null,
                _externalConceptList: null,
                _matchesDialog: null,

                buildRendering: function () {
                    this.inherited(arguments);
                },

                postCreate: function () {
                    this.inherited(arguments);

                    this._matches = [];
                    this.broadMatchList = new ConceptDetailList({}, this.broadMatchListNode);
                    this.closeMatchList = new ConceptDetailList({}, this.closeMatchListNode);
                    this.exactMatchList = new ConceptDetailList({}, this.exactMatchListNode);
                    this.narrowMatchList = new ConceptDetailList({}, this.narrowMatchListNode);
                    this.relatedMatchList = new ConceptDetailList({}, this.relatedMatchListNode);

                    var self = this;
                    new Button({
                        label: "Add " + this.title,
                        showLabel: true,
                        iconClass: 'plusIcon',
                        onClick: function () {
                            if (!self._matchesDialog) {
                                self._matchesDialog = self._createDialog();
                            }
                            self._matchesDialog.show();
                        }
                    }, this.matchesButton);

                    self.broadMatchList.on("relation.delete", function(evt){
                        self._removeMatch(evt.relation);
                    });
                    self.closeMatchList.on("relation.delete", function(evt){
                        self._removeMatch(evt.relation);
                    });
                    self.exactMatchList.on("relation.delete", function(evt){
                        self._removeMatch(evt.relation);
                    });
                    self.narrowMatchList.on("relation.delete", function(evt){
                        self._removeMatch(evt.relation);
                    });
                    self.relatedMatchList.on("relation.delete", function(evt){
                        self._removeMatch(evt.relation);
                    });
                },

                _addMatch: function (match) {
                    var found = arrayUtil.some(this._matches, function (item) {
                        return item.data.id == match.data.id;
                    });
                    if (!found) {
                        this._matches.push(match);
                        this._createNodeList();
                        return true;
                    }
                    return false;
                },

                _removeMatch: function (matchToDelete) {
                    var self = this;
                    arrayUtil.forEach(this._matches, function(match) {
                        if(match.data.uri == matchToDelete.sublabel) {
                          var position = arrayUtil.indexOf(self._matches, match);
                          self._matches.splice(position, 1);
                        }
                    });
                },

                _createNodeList: function () {
                    var matches = this._matches;

                    this.broadMatchList.buildList(
                        this.broadMatchList.mapMatchesForList(matches, "broadMatch"),
                        "Broad matches", false, true
                    );
                    this.closeMatchList.buildList(
                        this.closeMatchList.mapMatchesForList(matches, "closeMatch"),
                        "Close matches", false, true
                    );
                    this.exactMatchList.buildList(
                        this.exactMatchList.mapMatchesForList(matches, "exactMatch"),
                        "Exact matches", false, true
                    );
                    this.narrowMatchList.buildList(
                        this.narrowMatchList.mapMatchesForList(matches, "narrowMatch"),
                        "Narrow matches", false, true
                    );
                    this.relatedMatchList.buildList(
                        this.relatedMatchList.mapMatchesForList(matches, "relatedMatch"),
                        "Reated matches", false, true
                    );
                },

                _createDialog: function () {
                    var self = this;

                    var dlg = new Dialog({
                        style: "width: 600px",
                        title: "Choose a match",
                        doLayout: true
                    });

                    var extSchemeStore = new Memory({
                        idProperty: "id",
                        data: this.thesauri.externalSchemelist
                    });

                    var searchDiv = domConstruct.create("div", {}, dlg.containerNode);

                    domConstruct.create("p", {
                        'innerHTML': "Select an external scheme and enter a label to search for a match:"
                    }, searchDiv);
                    var selectScheme = new Select({
                        name: "extSchemeSelect",
                        store: extSchemeStore,
                        style: "width: 200px;",
                        title: "Select external scheme",
                        labelAttr: "name",
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
                            self._searchForConcepts(selectScheme.value, textFilter.value)
                        }
                    }).placeAt(searchDiv);

                    var listHolder = domConstruct.create("div", {}, searchDiv);
                    var list = new (declare([dgridList, dgridKeyboard, dgridSelection, DijitRegistry]))({
                        selectionMode: "single",
                        renderRow: function(object, options){
                            return domConstruct.create("div", {
                                innerHTML: object.label + " <em>(" + object.type + ", id: " + object.id + ")</em>"
                            });
                        }
                    }, listHolder);
                    list.renderArray([]);
                    this._externalConceptList = list;

                    var selectType = new Select({
                        name: "typeSelect",
                        options: [
                            {label: "Broad", value: "broadMatch"},
                            {label: "Close", value: "closeMatch"},
                            {label: "Exact", value: "exactMatch"},
                            {label: "Narrow", value: "narrowMatch"},
                            {label: "Related", value: "relatedMatch"}
                        ],
                        style: "width: 200px;",
                        title: "Select match type",
                        maxHeight: -1, // tells _HasDropDown to fit menu within viewport
                        onChange: function(value){
                            console.log(value);
                        }
                    }).placeAt(searchDiv);

                    var actionBar = domConstruct.create("div", {
                        'class': "dijitDialogPaneActionBar",
                        width: "300px"
                    }, dlg.containerNode);

                    var addBtn = new Button({
                        "label": "Add"
                    }).placeAt(actionBar);
                    var cancelBtn = new Button({
                        "label": "Cancel"
                    }).placeAt(actionBar);

                    addBtn.onClick = function () {
                        var row = null;
                        for(var id in list.selection){
                            if(list.selection[id]){
                                row = list.row(id);
                            }
                        }
                        var match = {
                            data: row.data,
                            type: selectType.get('value')
                        };
                        self._addMatch(match);
                        dlg.hide();
                    };

                    cancelBtn.onClick = function () {
                        dlg.hide();
                    };

                    on(dlg, "hide", function () {
                        selectType.reset();
                        textFilter.reset();
                        list.clearSelection();
                    });

                    return dlg
                },

                reset: function () {
                    this._matches = [];
                    this._createNodeList();
                },

                getMatches: function () {
                    var matches = {};
                    var types = ['broadMatch', 'closeMatch', 'exactMatch', 'narrowMatch', 'relatedMatch'];
                    var self = this;
                    arrayUtil.forEach(types, function(type) {
                        var uris = self.getMatchesUris(type);
                        if (uris.length > 0) {
                            matches[type] = uris;
                        }
                    });
                    console.log('matches:');
                    console.log(matches);
                    return matches;
                },

                getMatchesUris: function (type) {
                    var filteredMatches = arrayUtil.filter(this._matches, function(match){
                        return match.type == type;
                    });

                    return arrayUtil.map(filteredMatches, function (match) {
                        return match.data.uri;
                    });
                },

                setRelations: function (relations) {
                    this._matches = relations;
                    this._createNodeList();
                },

                setMatches: function (groupedMatches) {
                    var matchesUris = [];
                    var types = ['broadMatch', 'closeMatch', 'exactMatch', 'narrowMatch', 'relatedMatch'];
                    arrayUtil.forEach(types, function(type) {
                        if (groupedMatches[type]) {
                            matchesUris.concat(matches[type]);
                        }
                    });
                    console.log(matchesUris);
                    //todo: fetch matches with uris
                },

                close: function () {
                    domStyle.set(this.domNode, "display", "none");
                },

                open: function () {
                    domStyle.set(this.domNode, "display", "block");
                },

                _searchForConcepts: function (scheme, value) {
                    var self = this;
                    var url = "/conceptschemes/" + scheme + "/c?label=" + value + "&type=all&sort=+label";
                    xhr.get(url, {
                        handleAs: "json",
                        headers: {'Accept' : 'application/json'}
                    }).then(function(data){
                        self._externalConceptList.refresh();
                        self._externalConceptList.renderArray(data);
                    }, function(err){
                        console.error(err);
                    });
                }
            });
    });
