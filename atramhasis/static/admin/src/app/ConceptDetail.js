define([
    'dojo/_base/declare',
    "dojo/_base/array",
    "dojo/dom-construct",
    "dojo/dom-class",
    "dojo/on",
    "dojo/topic",
    'dijit/_WidgetBase',
    'dijit/_TemplatedMixin',
    'dijit/_WidgetsInTemplateMixin',
    "dijit/ConfirmDialog",
     "dojo/topic",
    "./form/ConceptDetailList",
    'dojo/text!./templates/ConceptDetail.html',
    "dijit/TitlePane"
], function (declare, arrayUtil, domConstruct, domClass, on, topic, _WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin, ConfirmDialog,topic,ConceptDetailList, template) {
    return declare([_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin], {

        templateString: template,

        baseClass: "conceptDetail",
        listNode: this.labelNode,
        conceptid: "",
        label: "",
        type: "",
        uri: "",
        schemeid: "",
        labels: [],
        notes: [],
        narrower: [],
        related: [],
        broader: [],
        members: [],
        member_of: [],


        postCreate: function () {



           var self = this;

           self.prefLabelList = new ConceptDetailList({ }, self.prefLabelListNode);
           self.altLabelList = new ConceptDetailList({}, self.altLabelListNode);
           self.hiddenLabelList = new ConceptDetailList({}, self.hiddenLabelListNode);
           self.changeNoteList = new ConceptDetailList({ }, self.changeNoteListNode);
           self.definitionList = new ConceptDetailList({}, self.definitionListNode);
           self.editorialNoteList = new ConceptDetailList({}, self.editorialNoteListNode);
           self.exampleList = new ConceptDetailList({ }, self.exampleListNode);
           self.historyNoteList = new ConceptDetailList({}, self.historyNoteListNode);
           self.scopeNoteList = new ConceptDetailList({}, self.scopeNoteListNode);
           self.noteList = new ConceptDetailList({}, self.noteListNode);
           self.memberofList = new ConceptDetailList({}, self.memberofListNode);
           self.broaderList = new ConceptDetailList({}, self.broaderListNode);
           self.narrowerList = new ConceptDetailList({}, self.narrowerListNode);
           self.relatedList = new ConceptDetailList({}, self.relatedListNode);
           self.membersList = new ConceptDetailList({}, self.membersListNode);
           self.memberofList = new ConceptDetailList({}, self.memberofListNode);


            var actionNode = this.actionNode;

            var deleteLi = domConstruct.create("li", {
                innerHTML: "<a href='#'>Delete</a>"
            }, actionNode);
            var editLi = domConstruct.create("li", {
                innerHTML: "<a href='#'>Edit</a>"
            }, actionNode);

            on(deleteLi, "click", function (evt) {
                evt.preventDefault();

                var myDialog = new ConfirmDialog({
                    title: "Delete",
                    content: "Are you sure you want to delete this?",
                    style: "width: 200px"
                });
                on(myDialog, "execute", function () {
                    topic.publish("concept.delete", self.conceptid);
                });
                on(myDialog, "cancel", function () {
                    //do nothing, will be destroyed on hide
                });
                on(myDialog, "hide", function () {
                    myDialog.destroyRecursive();
                });
                myDialog.show();

                return false;
            });

            on(editLi, "click", function (evt) {
                evt.preventDefault();
                topic.publish("concept.edit", self.conceptid);
                return false;
            });

            self.prefLabelList.buidList(self.prefLabelList.mapLabelsForList(self.labels, "prefLabel"), "Preferred labels", false);
            self.altLabelList.buidList(self.altLabelList.mapLabelsForList(self.labels, "altLabel"), "Alternate labels", false);
            self.hiddenLabelList.buidList( self.hiddenLabelList.mapLabelsForList(self.labels, "hiddenLabel"), "Hidden labels", false);

            self.definitionList.buidList(self.definitionList.mapNotesForList(self.notes, "definition"), "Definition", false);
            self.changeNoteList.buidList(self.changeNoteList.mapNotesForList(self.notes, "changeNote"), "Change note", false);
            self.editorialNoteList.buidList(self.editorialNoteList.mapNotesForList(self.notes, "editorialNote"), "Editorial note", false);
            self.exampleList.buidList( self.exampleList.mapNotesForList(self.notes, "example"), "Example", false);
            self.historyNoteList.buidList(self.historyNoteList.mapNotesForList(self.notes, "historyNote"), "Historynote", false);
            self.scopeNoteList.buidList(self.scopeNoteList.mapNotesForList(self.notes, "scopeNote"), "Scopenote", false);
            self.noteList.buidList(self.noteList.mapNotesForList(self.notes, "note"), "Note", false);

            self.broaderList.buidList(self.broaderList.mapRelationsForList(self.broader), "Broader", true);
            self.narrowerList.buidList(self.narrowerList.mapRelationsForList(self.narrower), "Narrower", true);
            self.relatedList.buidList(self.relatedList.mapRelationsForList(self.related), "Related", true);
            self.membersList.buidList(self.membersList.mapRelationsForList(self.members), "Members", true);
            self.memberofList.buidList(self.memberofList.mapRelationsForList(self.member_of), "Member of", true);

      /*      this._buidList(this.prefLabelListNode, this._mapLabelsForList(this.labels, "prefLabel"), "Preferred labels", false);
            this._buidList(this.altLabelListNode, this._mapLabelsForList(this.labels, "altLabel"), "Alternate labels", false);
            this._buidList(this.hiddenLabelListNode, this._mapLabelsForList(this.labels, "hiddenLabel"), "Hidden labels", false);

            this._buidList(this.definitionListNode, this._mapNotesForList(this.notes, "definition"), "Definition", false);
            this._buidList(this.changeNoteListNode, this._mapNotesForList(this.notes, "changeNote"), "Change note", false);
            this._buidList(this.editorialNoteListNode, this._mapNotesForList(this.notes, "editorialNote"), "Editorial note", false);
            this._buidList(this.exampleListNode, this._mapNotesForList(this.notes, "example"), "Example", false);
            this._buidList(this.historyNoteListNode, this._mapNotesForList(this.notes, "historyNote"), "Historynote", false);
            this._buidList(this.scopeNoteListNode, this._mapNotesForList(this.notes, "scopeNote"), "Scopenote", false);
            this._buidList(this.noteListNode, this._mapNotesForList(this.notes, "note"), "Note", false);

            this._buidList(this.broaderListNode, this._mapRelationsForList(this.broader), "Broader", true);
            this._buidList(this.narrowerListNode, this._mapRelationsForList(this.narrower), "Narrower", true);
            this._buidList(this.relatedListNode, this._mapRelationsForList(this.related), "Related", true);
            this._buidList(this.membersListNode, this._mapRelationsForList(this.members), "Members", true);
            this._buidList(this.memberofListNode, this._mapRelationsForList(this.member_of), "Member of", true);*/

             topic.subscribe("conceptDetail.refresh",function (refreshedConcept) {




             });

        },
        _refreshConceptDetail:function()
        {

        },
        _mapLabelsForList: function (labels, type) {
            var filteredItems = arrayUtil.filter(labels, function (item) {
                return item.type == type;
            });
            return arrayUtil.map(filteredItems, function (item) {
                return {"id": "", "mainlabel": item.label, "sublabel": item.language};
            });
        },

        _mapNotesForList: function (notes, type) {
            var filteredItems = arrayUtil.filter(notes, function (item) {
                return item.type == type;
            });
            return arrayUtil.map(filteredItems, function (item) {
                return {"id": "", "mainlabel": item.note, "sublabel": item.language};
            });
        },

        _mapRelationsForList: function (relations) {
            return arrayUtil.map(relations, function (item) {
                return {"id": item.id, "mainlabel": item.label, "sublabel": item.id};
            });
        },

        _buidList: function (node, items, title, clickable) {
            if (items && items.length > 0) {

                domConstruct.place("<h3>" + title + ":</h3>", node, "first");
                var ul = domConstruct.create("ul", {
                    className: 'conceptlist'
                }, node);

                var scheme = this.schemeid;

                var sortedItems = items.sort(function (a, b) {
                    var nameA = a.mainlabel.toLowerCase(), nameB = b.mainlabel.toLowerCase();
                    if (nameA < nameB) //sort string ascending
                        return -1;
                    if (nameA > nameB)
                        return 1;
                    return 0; //default return value (no sorting)
                });

                arrayUtil.forEach(sortedItems, function (item) {
                    var li = domConstruct.create("li", {
                        innerHTML: item.mainlabel + " (<em>" + item.sublabel + "</em>)"
                    }, ul);
                    if (clickable) {
                        domClass.add(li, "clickable");
                        on(li, "click", function () {
                            topic.publish("concept.open", item.id, scheme);
                        });
                    }
                });
            }
        }
    });
});