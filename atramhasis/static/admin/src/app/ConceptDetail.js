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
    "./form/ConceptDetailList",
    'dojo/text!./templates/ConceptDetail.html',
    "dijit/TitlePane"
], function (declare, arrayUtil, domConstruct, domClass, on, topic, _WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin, ConfirmDialog, ConceptDetailList, template) {
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
        matches: [],


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
           self.broaderList = new ConceptDetailList({}, self.broaderListNode);
           self.narrowerList = new ConceptDetailList({}, self.narrowerListNode);
           self.relatedList = new ConceptDetailList({}, self.relatedListNode);
           self.membersList = new ConceptDetailList({}, self.membersListNode);
           self.memberofList = new ConceptDetailList({}, self.memberofListNode);
           self.broadMatchList = new ConceptDetailList({}, self.broadMatchListNode);
           self.closeMatchList = new ConceptDetailList({}, self.closeMatchListNode);
           self.exactMatchList = new ConceptDetailList({}, self.exactMatchListNode);
           self.narrowMatchList = new ConceptDetailList({}, self.narrowMatchListNode);
           self.relatedMatchList = new ConceptDetailList({}, self.relatedMatchListNode);


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

             self._CreateNodeLists();
             topic.subscribe("conceptDetail.refresh",function (refreshedConcept)
             {
                 self._refreshConceptDetail(refreshedConcept);

             });

        },
        _refreshConceptDetail:function(refreshedConcept)
        {
            var self=this;
            self.labels=refreshedConcept.labels;
            self.notes=refreshedConcept.notes;
            self.broader=refreshedConcept.broader;
            self.narrower=refreshedConcept.narrower;
            self.related=refreshedConcept.related;
            self.members=refreshedConcept.members;
            self.member_of=refreshedConcept.member_of;
            self.matches=refreshedConcept.matches;
            self._CreateNodeLists();
        },

        _CreateNodeLists:function()
        {
            var self=this;
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

            self.broaderList.schemeid=self.schemeid;
            self.narrowerList.schemeid=self.schemeid;
            self.relatedList.schemeid=self.schemeid;
            self.membersList.schemeid=self.schemeid;
            self.memberofList.schemeid=self.schemeid;

            self.broaderList.buidList(self.broaderList.mapRelationsForList(self.broader), "Broader", true);
            self.narrowerList.buidList(self.narrowerList.mapRelationsForList(self.narrower), "Narrower", true);
            self.relatedList.buidList(self.relatedList.mapRelationsForList(self.related), "Related", true);
            self.membersList.buidList(self.membersList.mapRelationsForList(self.members), "Members", true);
            self.memberofList.buidList(self.memberofList.mapRelationsForList(self.member_of), "Member of", true);

            self.broadMatchList.buidList(self.broadMatchList.mapMatchesForList(self.matches, "broadMatch"), "BroadMatch", false);
            self.closeMatchList.buidList(self.closeMatchList.mapMatchesForList(self.matches, "closeMatch"), "CloseMatch", false);
            self.exactMatchList.buidList(self.exactMatchList.mapMatchesForList(self.matches, "exactMatch"), "ExactMatch", false);
            self.narrowMatchList.buidList(self.narrowMatchList.mapMatchesForList(self.matches, "narrowMatch"), "NarrowMatch", false);
            self.relatedMatchList.buidList(self.relatedMatchList.mapMatchesForList(self.matches, "relatedMatch"), "RelatedMatch", false);

        }
    });
});
