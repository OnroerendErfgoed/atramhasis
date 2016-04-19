define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/dom-style',
  'dojo/json',
  'dojo/on',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/ConceptDetail.html',
  '../dialogs/ConceptEditDialog'
], function (
  declare,
  array,
  lang,
  domConstruct,
  domClass,
  domStyle,
  JSON,
  on,
  _WidgetBase,
  _TemplatedMixin,
  template,
  ConceptEditDialog
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'concept-detail',
    concept: null,
    scheme: null,
    maxHeight: null,
    languageController: null,
    listController: null,
    conceptSchemeController: null,
    _editDialog: null,

    postCreate: function () {
      this.inherited(arguments);
      console.debug('ConceptDetail::postCreate');
    },

    startup: function () {
      this.inherited(arguments);
      console.debug('ConceptDetail::startup');

      this._setData(this.concept);
      domStyle.set(this.conceptDetailNode, 'max-height', (this.maxHeight ? this.maxHeight + 'px' : '500px'));
    },

    _openEditDialog: function () {
      console.debug('ConceptDetail::_openEditDialog');
      this._editDialog = new ConceptEditDialog({
        concept: this.concept,
        scheme: this.scheme,
        parent: this,
        languageController: this.languageController,
        listController: this.listController,
        conceptSchemeController: this.conceptSchemeController
      });
      on(this._editDialog, 'concept.save', lang.hitch(this, function(evt) {
        console.log(evt);
        this.emit('concept.save', {
          concept: evt.concept,
          schemeId: evt.schemeId
        });
      }));
      this._editDialog.startup();
    },

    _setData: function(concept) {
      // set view data
      this.conceptTitleViewNode.innerHTML = '<strong>' + this.scheme + ' : ' + concept.label + '</strong>';
      this.idViewNode.innerHTML = 'ID: ' + concept.id;
      this.typeViewNode.innerHTML = 'TYPE: ' + concept.type;
      this.uriViewNode.innerHTML = 'URI: ';
      domConstruct.create('a', { href: this.concept.uri, innerHTML: this.concept.uri, target: '_blank' }, this.uriViewNode);

      if (concept.labels && concept.label.length > 0) {
        var pref = '';
        var alt = '';
        array.forEach(concept.labels, lang.hitch(this, function(label) {
          if (label.type === 'prefLabel') {
            pref += label.label + ' (' + label.language + '), ';
          }
          if (label.type === 'altLabel') {
            alt += label.label + ' (' + label.language + '), ';
          }
        }));
        if (alt.length > 2) {
          alt = alt.substring(0, alt.length - 2);
        }
        if (pref.length > 2) {
          pref = pref.substring(0, pref.length - 2);
        }
        this.preferredLabelsNode.innerHTML = pref;
        this.alternateLabelsNode.innerHTML = alt;
      }

      if (concept.narrower && concept.narrower.length > 0) {
        var dt = domConstruct.create('dt', { innerHTML: 'Narrower' }, this.relationsListNode, 'first');
        var narrowString = '';
        array.forEach(concept.narrower, lang.hitch(this, function(narrow) {
          narrowString += '<a href="' + narrow.uri + '" target="_blank" >' + narrow.label + '</a> (' + narrow.id + '), '
        }));
        if (narrowString.length > 2) {
          narrowString = narrowString.substring(0, narrowString.length - 2);
        }
        domConstruct.create('dd', {innerHTML: narrowString}, dt);
      }


      if (concept.broader && concept.broader.length > 0) {
        var dt = domConstruct.create('dt', { innerHTML: 'Broader' }, this.relationsListNode, 'last');
        var broadString = '';
        array.forEach(concept.broader, lang.hitch(this, function(broader) {
          broadString += '<a href="' + broader.uri + '" target="_blank" >' + broader.label + '</a> (' + broader.id + '), '
        }));
        if (broadString.length > 2) {
          broadString = broadString.substring(0, broadString.length - 2);
        }
        domConstruct.create('dd', {innerHTML: broadString}, dt);
      }

      if (concept.related && concept.related.length > 0) {
        var dt = domConstruct.create('dt', { innerHTML: 'Related' }, this.relationsListNode, 'last');
        var relatedString = '';
        array.forEach(concept.related, lang.hitch(this, function(related) {
          relatedString += '<a href="' + related.uri + '" target="_blank" >' + related.label + '</a> (' + related.id + '), '
        }));
        if (relatedString.length > 2) {
          relatedString = relatedString.substring(0, relatedString.length - 2);
        }
        domConstruct.create('dd', {innerHTML: relatedString}, dt);
      }

      //TODO matches


      if (concept.notes && concept.notes.length > 0) {
        array.forEach(concept.notes, lang.hitch(this, function(note) {
          domConstruct.create('li', {
            lang: note.language,
            innerHTML: '<strong>' + this._capitalize(note.type) + '</strong> <em>(' + note.language + ')</em>: ' + note.note
          }, this.scopeNoteNode, 'last');
        }));
      } else {
        domConstruct.destroy(this.scopeNoteNode);
      }
    },

    _capitalize: function (s) {
      // returns the first letter capitalized + the string from index 1 and out aka. the rest of the string
      return s[0].toUpperCase() + s.substr(1);
    },

    _closeEditDialog: function() {
      if (this._editDialog) {
        this._editDialog._close();
        this._editDialog.destroyRecursive();
      }
    }
  });
});