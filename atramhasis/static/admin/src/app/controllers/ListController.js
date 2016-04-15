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
      {label: "Hidden", value: "hiddenLabel"}
    ],
    noteTypes: [
      {label: "Definition", value: "definition"},
      {label: "Note", value: "note"}
    ],


    constructor: function (args) {
      console.debug('ConceptController::constructor');
      declare.safeMixin(this, args);
    },

    getLabelTypes: function() {
      return this.labelTypes;
    },

    getNoteTypes: function() {
      return this.noteTypes;
    }

  });
});
