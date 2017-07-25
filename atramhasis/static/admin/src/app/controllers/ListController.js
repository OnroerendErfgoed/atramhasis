/**
 * @module controllers/ListController
 */
define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/request/xhr',
  'dojo/Deferred',
  'dstore/Rest'
], function (
  declare,
  lang,
  array,
  xhr,
  Deferred,
  Rest
) {
  return declare(null, {

    labelTypes: [
      {label: "Preferred", value: "prefLabel"},
      {label: "Alternative", value: "altLabel"},
      {label: "Hidden", value: "hiddenLabel"},
      {label: "Sort", value: "sortLabel"}
    ],
    noteTypes: [
      {label: "Definition", value: "definition"},
      {label: "Note", value: "note"},
      {label: 'History note', value: 'historyNote'},
      {label: 'Scope note', value: 'scopeNote'}
    ],
    matchTypes: [
      {label: "Broad", value: "broad"},
      {label: "Close", value: "close"},
      {label: "Exact", value: "exact"},
      {label: "Narrow", value: "narrow"},
      {label: "Related", value: "related"}
    ],
    conceptTypes: [
      {label: 'Concept', value: 'concept'},
      {label: 'Collection', value: 'collection'}
    ],

    constructor: function (args) {
      console.debug('ListController::constructor');
      declare.safeMixin(this, args);
    },

    getLabelTypes: function() {
      return this.labelTypes;
    },

    getNoteTypes: function() {
      return this.noteTypes;
    },

    getMatchTypes: function() {
      return this.matchTypes;
    },

    getConceptTypes: function() {
      return this.conceptTypes;
    }

  });
});
