define([
    'dojo/_base/declare',
    "dojo/_base/array",
    "dojo/dom-construct",
    "dojo/query",
    "dojo/on",

    'dijit/_WidgetBase',
    'dijit/_TemplatedMixin',

    'dojo/text!./templates/ConceptDetail.html'

], function (
    declare, arrayUtil, domConstruct, query, on,

    _WidgetBase,
    _TemplatedMixin,

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