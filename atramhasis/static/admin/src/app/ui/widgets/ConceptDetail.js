define([
  'dojo/_base/declare',
  'dojo/_base/array',
  'dojo/_base/lang',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/dom-style',
  'dojo/json',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./templates/ConceptDetail.html'
], function (
  declare,
  array,
  lang,
  domConstruct,
  domClass,
  domStyle,
  JSON,
  _WidgetBase,
  _TemplatedMixin,
  template
) {
  return declare([_WidgetBase, _TemplatedMixin], {

    templateString: template,
    baseClass: 'concept-detail',
    concept: null,
    scheme: null,
    maxHeight: null,

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

    _setData: function(concept) {
      // set view data
      this.conceptTitleViewNode.innerHTML = '<strong>' + this.scheme + ' : ' + concept.label + '</strong>';
      this.idViewNode.innerHTML = 'ID: ' + concept.id;
      this.typeViewNode.innerHTML = 'TYPE: ' + concept.type;
      this.uriViewNode.innerHTML = 'URI: ';
      domConstruct.create('a', { href: this.concept.uri, innerHTML: this.concept.uri, target: '_blank' }, this.uriViewNode);

      if (concept.labels && concept.label.length > 0) {
        array.forEach(concept.labels, lang.hitch(this, function(label) {
          var pref = '';
          var alt = '';
          if (label.type === 'prefLabel') {
            pref += label.label + ' (' + label.language + '), ';
          }
          if (label.type === 'altLabel') {
            alt += label.label + ' (' + label.language + '), ';
          }

          if (alt.length > 2) {
            alt = alt.substring(0, alt.length - 2);
          }
          if (pref.length > 2) {
            pref = pref.substring(0, pref.length - 2);
          }

          this.preferredLabelsNode.innerHTML = pref;
          this.alternateLabelsNode.innerHTML = alt;
        }));
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

      // notes
      //{%- for note in concept.notes %}
      //<li lang="{{ note.language }}">
      //  <strong>{{ note.notetype_id|capitalize }}</strong> <em>({{ note.language }})</em>: {{ note.note|safe }}
      //</li>
      //{%- endfor %}

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
    }
  });
});