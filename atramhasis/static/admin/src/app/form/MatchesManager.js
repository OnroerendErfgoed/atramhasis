define([
        "dojo/_base/declare",
        "dijit/Dialog",
        "dijit/_WidgetBase",
        "dijit/_TemplatedMixin",
        "dijit/form/Button",
        "dijit/form/Select",
        "dgrid/OnDemandGrid",
        "dijit/form/TextBox",
        "dojox/layout/TableContainer",
        "dojo/_base/lang",
        "dojo/dom-construct",
        "dojo/store/Memory",
        "dgrid/editor",
        "dgrid/extensions/ColumnHider",
        "dojo/_base/array",
        "dojo/on",
        "dojo/dom-style",
        "./ConceptDetailList",
        "dojo/text!./templates/MatchesManager.html"

    ],
    function (declare, Dialog, WidgetBase, TemplatedMixin, Button, Select, OnDemandGrid, TextBox, TableContainer, lang, domConstruct, Memory, editor, ColumnHider, arrayUtil, on, domStyle, ConceptDetailList, template) {
        return declare(
            "app/form/MatchesManager",
            [WidgetBase, TemplatedMixin],
            {
                templateString: template,

                name: 'MatchesManager',
                title: 'Matches:',
                matchesGrid: null,
                matchUri: null,
                matchTypeComboBox: null,
                matches: null,
                tempMatches: null,//this variable is used to recover the matches if user delete a match and then press on the cancel button
                EditMatchesButton: null,

                buildRendering: function () {
                    this.inherited(arguments);
                },
                postCreate: function () {
                    this.inherited(arguments);
                    var self = this;
                    //noinspection CommaExpressionJS

                    self.EditMatchesButton = new Button({
                        label: "Add Matches",
                        showLabel: true,
                        iconClass: 'plusIcon',
                        onClick: function () {
                            var dlg = self._createDialog();
                            if (self.matches) {
                                self._setGrid(self.matches);
                                self.tempMatches = lang.clone(self.matches);
                            }
                            dlg.show();
                            self.matchesGrid.resize();
                            self.matchesGrid.refresh();
                        }
                    }, this.matchesButton);

                    this.broadMatchList = new ConceptDetailList({}, this.broadMatchListNode);
                    this.closeMatchList = new ConceptDetailList({}, this.closeMatchListNode);
                    this.exactMatchList = new ConceptDetailList({}, this.exactMatchListNode);
                    this.narrowMatchList = new ConceptDetailList({}, this.narrowMatchListNode);
                    this.relatedMatchList = new ConceptDetailList({}, this.relatedMatchListNode);

                },

                _createDialog: function () {
                    var self = this;
                    var dlg = new Dialog({
                        style: "width: 600px",
                        title: "Add Matches",
                        doLayout: true
                    });

                    var mainDiv = domConstruct.create("div");
                    domConstruct.place(mainDiv, dlg.containerNode);
                    var tableBoxDiv = domConstruct.create("div");
                    domConstruct.place(tableBoxDiv, mainDiv, "first");
                    var labelTabForBoxes = new TableContainer({cols: 4, spacing: 10, orientation: "vert"}, tableBoxDiv);


                    var matchType = this._getMatchType();

                    var matchTypeComboBox = new Select(
                        {
                            id: "TypeComboBox",
                            name: "matchTypeComboBox",
                            title: "Type of match:",
                            placeHolder: 'Select a type',
                            options: matchType,
                            style: { width: '120px' }

                        });

                    var addMatchButtonToTable = new Button
                    (
                        {
                            iconClass: 'plusIcon',
                            showLabel: false,
                            onClick: lang.hitch(this, function () {

                                console.log("Add match to tabel in add match dialog");

                                self.matchesGrid.store.add({
                                    uri: self.matchUri.get('value'),
                                    type:self.matchTypeComboBox.get('value') ,
                                    typeDisplayed: self.matchTypeComboBox.get('displayedValue')});
                                self.matchesGrid.resize();
                                self.matchesGrid.refresh();
                            })
                        }
                    );

                    var matchUri = new TextBox({id: "matchUri", title: "URI:"});

                    self.matchUri = matchUri;
                    self.matchTypeComboBox = matchTypeComboBox;

                    labelTabForBoxes.addChild(matchUri);
                    labelTabForBoxes.addChild(matchTypeComboBox);
                    labelTabForBoxes.addChild(addMatchButtonToTable);
                    labelTabForBoxes.startup();

                    var gridDiv = domConstruct.create("div");
                    var matchesGrid = this._createGrid(gridDiv);
                    domConstruct.place(gridDiv, mainDiv, "last");

                    self.matchesGrid = matchesGrid;

                    var actionBar = domConstruct.create("div", {
                        'class': "dijitDialogPaneActionBar"
                    }, dlg.containerNode);

                    var addBtn = new Button({
                        "label": "Save"
                    }).placeAt(actionBar);
                    var cancelBtn = new Button({
                        "label": "Cancel"
                    }).placeAt(actionBar);

                    addBtn.onClick = function () {
                        self._createNodeList(self.matchesGrid.store.data);
                        self.matches = self.matchesGrid.store.data;
                        self.setEditMatchesButton();
                        dlg.hide();
                    };
                    cancelBtn.onClick = function () {
                        self.matches = lang.clone(self.tempMatches);
                        dlg.hide();
                    };

                    on(dlg, "hide", function () {
                        matchUri.destroy();
                        matchTypeComboBox.destroy();
                    });

                    return dlg;


                },

                _getMatchType: function () {

                    var Type = [
                        {label: "Broad", value: "broadMatch"},
                        {label: "Close", value: "closeMatch"},
                        {label: "Exact", value: "exactMatch"},
                        {label: "Narrow", value: "narrowMatch"},
                        {label: "Related", value: "relatedMatch"}
                    ];

                    return Type;
                },


                _createGrid: function (gridDiv) {
                    var self = this;
                    var columns;
                    columns = [
                        {label: "URI", field: "uri"},
                        {label: "Type", field: "typeDisplayed"},
                        {label: "Type", field: "type", unhidable: true, hidden: true},
                        editor({label: " ", field: 'button',
                                editorArgs: {label: "delete", showLabel: false, iconClass: 'minIcon', onClick: function (event) {
                                    var row = grid.row(event);
                                    var itemToDelete = row.data.id;
                                    grid.store.remove(itemToDelete);
                                    grid.resize();
                                    grid.refresh();
                                }
                                }},
                            Button)
                    ];
                    var gridStore = new Memory({
                        data: []

                    });
                    var grid = new (declare([OnDemandGrid, ColumnHider]))({
                        columns: columns,
                        store: gridStore,
                        selectionMode: "single" // for Selection; only select a single row at a time
                    }, gridDiv);

                    grid.startup();

                    return grid;
                },
                _createNodeList: function (matches) {
                    var matchObject = this._mapMatchesToMatchObject(matches);
                    var mappedMatches = this.broadMatchList.mapMatchesForList(matchObject, "broadMatch");
                    this.broadMatchList.buidList(mappedMatches, "Broad matches", false);
                    mappedMatches = this.closeMatchList.mapMatchesForList(matchObject, "closeMatch");
                    this.closeMatchList.buidList(mappedMatches, "Close matches", false);
                    mappedMatches = this.exactMatchList.mapMatchesForList(matchObject, "exactMatch");
                    this.exactMatchList.buidList(mappedMatches, "Exact matches", false);
                    mappedMatches = this.narrowMatchList.mapMatchesForList(matchObject, "narrowMatch");
                    this.narrowMatchList.buidList(mappedMatches, "Narrow matches", false);
                    mappedMatches = this.relatedMatchList.mapMatchesForList(matchObject, "relatedMatch");
                    this.relatedMatchList.buidList(mappedMatches, "Related matches", false);
                },
                _setGrid: function (matches) {
                    var gridStore = new Memory({
                        data: matches
                    });
                    this.matchesGrid.set("store", gridStore);
                },
                _mapMatchToDisplayedMatch: function (matches, typevalue, typeToBeDisplayed) {
                    return arrayUtil.map(matches, function (item) {
                        return {uri: item, type: typevalue, typeDisplayed: typeToBeDisplayed};
                    });
                },

                getMatches: function () {
                    if(this.matchesGrid)
                    {
                        return this._mapMatchesToMatchObject(this.matchesGrid.store.data);
                    }
                    else
                    {
                        return this._mapMatchesToMatchObject(this.matches);
                    }

                },

                setMatches: function (matches) {
                    console.log("set matches: " + matches);

                    this.matches = []

                    for(matchType in matches) {
                        this.matches.push.apply(this.matches, this._mapMatchToDisplayedMatch(matches[matchType], matchType, this._mapMatchTypeToDisplayType(matchType)));
                    }

                    this._createNodeList(this.matches);
                    this.tempMatches = lang.clone(this.matches);
                },

                _mapMatchTypeToDisplayType: function(matchType){
                    var label;
                    arrayUtil.forEach(this._getMatchType(), function(type, i) {
                        if(type.value == matchType){
                            label =  type.label;
                        }
                     });
                     return label;
                },

                _mapMatchesToMatchObject: function(matches){
                    var matchObject = {};
                    arrayUtil.forEach(matches, function(match, i) {
                        if(matchObject[match.type]){
                            matchObject[match.type].push(match.uri);
                        }else{
                            matchObject[match.type] = [match.uri];
                        }
                    });
                    return matchObject;
                },

                setEditMatchesButton: function () {
                    this.EditMatchesButton.set("label", "Edit matches");
                    this.EditMatchesButton.set("iconClass", "");

                },
                reset: function () {
                    this.broadMatchList.reset();
                    this.closeMatchList.reset();
                    this.exactMatchList.reset();
                    this.narrowMatchList.reset();
                    this.relatedMatchList.reset();
                    this.matches = null;
                    this.tempMatches = null;
                    this.matchesGrid=null;
                    this.EditMatchesButton.set("label", "Add matches");
                    this.EditMatchesButton.set("iconClass", "plusIcon");
                },
                close: function () {
                    domStyle.set(this.domNode, "display", "none");
                    this.reset();
                },

                open: function () {
                    domStyle.set(this.domNode, "display", "block");
                }
            });
    });
