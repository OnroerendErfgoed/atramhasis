define([
    'dojo/_base/declare',
    "dojo/_base/array",
    "dojo/dom-construct",
    "dojo/query",
    "dojo/on",
    "dojo/topic",

    'dijit/_WidgetBase',
    'dijit/_TemplatedMixin',
    "dijit/ConfirmDialog",

    'dojo/text!./templates/ConceptDetail.html'

], function (
    declare, arrayUtil, domConstruct, query, on, topic,

    _WidgetBase,
    _TemplatedMixin,

    ConfirmDialog,

    template
    ) {
    return declare([_WidgetBase, _TemplatedMixin], {

        templateString: template,

        baseClass: "conceptDetail",
        listNode: this.labelNode,
        conceptid: "",
        label: "",
        type: "",
        uri:"",
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

            var actionNode = this.actionNode;
            var deleteLi = domConstruct.create("li", {
                innerHTML: "<a href='#'>Delete</a>"
            }, actionNode);
            var editLi = domConstruct.create("li", {
                innerHTML: "<a href='#'>Edit</a>"
            }, actionNode);
            on(deleteLi, "click", function(evt){
                evt.preventDefault();

                var myDialog = new ConfirmDialog({
                    title: "Delete",
                    content: "Are you sure you want to delete this?",
                    style: "width: 200px"
                });
                on(myDialog, "cancel", function(){
                    console.log("confirmdialog cancel");
                });
                on(myDialog, "execute", function(){
                    console.log("concept.delete publish:" + self.conceptid);
                    topic.publish("concept.delete", self.conceptid, self.schemeid);
                });
                on(myDialog, "hide", function(){
                    console.log("confirmdialog destroy on hide");
                    myDialog.destroyRecursive();
                });
                myDialog.show();
                return false;
            });
            on(editLi, "click", function(evt){
                evt.preventDefault();
                console.log("concept.edit publish:" + self.conceptid);
                topic.publish("concept.edit", self.conceptid, self.schemeid);
                return false;
            });

            var labelListNode = this.labelListNode;
            arrayUtil.forEach(this.labels, function(label){
                console.log(label);
                domConstruct.create("li", {
                    innerHTML: label.label + " (<em>" + label.language + "</em>)"
                }, labelListNode);
            });
            var notesListNode = this.notesListNode;
            arrayUtil.forEach(this.notes, function(note){
                console.log(note);
                domConstruct.create("li", {
                    innerHTML: note.type + " (<em>" + note.language + "</em>): " + note.note
                }, notesListNode);
            });
            this._buildLinkList(this.narrowerListNode, this.narrower);

            this._buildLinkList(this.broaderListNode, this.broader);

            this._buildLinkList(this.relatedListNode, this.related);

            this._buildLinkList(this.membersListNode, this.members);

            this._buildLinkList(this.memberofListNode, this.member_of);
        },

        _buildLinkList: function(node, items){
            arrayUtil.forEach(items, function(item){
                var li = domConstruct.create("li", {
                    innerHTML: "<a href='#'>" + item + "</a>"
                }, node);
                on(query("a", li), "click", function(){
                    console.log("relation selected:" + this.innerHTML);
                });
            });
        }



    });
});