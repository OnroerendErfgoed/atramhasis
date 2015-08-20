define(
    [
        'dojo/_base/declare',
        'dojo/topic',
        'dojo/_base/lang',
        'dojo/text!./templates/EditConceptDialog.html',
        'dijit/_WidgetBase',
        'dijit/_TemplatedMixin',
        'dijit/_WidgetsInTemplateMixin',
        'dijit/Dialog',
        'dijit/form/TextBox',
        'dijit/form/Button',
        '../../form/LabelManager',
        '../../form/NoteManager'
    ],
    function (
        declare,
        topic,
        lang,
        template,
        _WidgetBase,
        _TemplatedMixin,
        WidgetsInTemplateMixin,
        Dialog,
        TextBox,
        Button,
        LabelManager,
        NoteManager) {
        return declare([
                _WidgetBase, WidgetsInTemplateMixin, _TemplatedMixin], {
                templateString: template,
                widgetsInTemplate: true,
                dialog: null,
                scheme: null,
                concept: null,
                thesauri: null,
                externalSchemeService: null,
                languageStore: null,
                conceptSchemeController: null,

                constructor: function (options) {
                    declare.safeMixin(this, options);
                    this.inherited(arguments)
                },

                postCreate: function () {
                    this.inherited(arguments);
                    this.dialog = new Dialog({
                        title: 'Edit concept scheme',
                        style: 'width: 400px',
                        draggable: false
                    });
                    this.labelManager = new LabelManager({
                        'name': 'lblMgr',
                        'languageStore': this.languageStore
                    }, this.labelContainerNode);
                    this.noteManager = new NoteManager({
                        'name': 'noteMgr',
                        'languageStore': this.languageStore
                    }, this.noteContainerNode);
                    this.schemebox = new TextBox({title: "Scheme:"}, this.conceptSchemaNode);
                    this.schemebox.set('disabled', true);

                    this.dialog.set('content', this);
                },

                startup: function () {
                    this.inherited(arguments);
                },

                _save: function(evt){
                    evt.preventDefault();
                    this.concept.labels = this.labelManager.getLabels();
                    this.concept.notes = this.noteManager.geNotes();
                    this.conceptSchemeController.editConceptScheme(this.concept).then(
                        lang.hitch(this, function (result) {
                            topic.publish('dGrowl', "The concept scheme has been saved",
                                {'title': "Succes", 'sticky': false, 'channel': 'info'});
                            this.dialog.hide();
                        }),
                        function (error) {
                            console.error(error);
                            topic.publish('dGrowl', "Something went wrong while saving the concept scheme",
                                {'title': "Error status: " + error.response.status, 'sticky': true, 'channel': 'error'});
                        }
                    );
                },

                _cancel: function (evt) {
                    evt.preventDefault();
                    this.dialog.hide();
                },

                reset: function(){
                    this.labelManager.reset();
                    this.noteManager.reset();
                },

                init: function (scheme) {
                    this.reset();
                    this.scheme = scheme;
                    this.schemebox.set('value', scheme);
                    this.conceptSchemeController.getConcept(scheme).then(
                        lang.hitch(this, function (concept) {
                            this.concept = concept;
                            topic.publish("concept.close", this.concept.id, scheme);
                            if (this.concept.labels) {
                                this.labelManager.setLabels(this.concept.labels);
                                if(this.concept.labels.length>0) {
                                    this.labelManager.SetEditLabelButton();
                                }
                            }
                            if (this.concept.notes)
                            {
                                this.noteManager.setNotes(this.concept.notes);
                                if(this.concept.notes.length>0) {
                                    this.noteManager.setEditNoteButton();
                                }
                            }
                            this.dialog.show();
                        }),
                        function (error) {
                            console.error(error);
                            topic.publish('dGrowl', "Something went wrong while opening the concept scheme",
                                {'title': "Error status: " + error.response.status, 'sticky': true, 'channel': 'error'});
                        }
                    );
                },

                addSuperordinate: function (superordinate) {
                    this.superordinatesManager.setRelations(superordinate);
                }
            }
        )
    }
);
