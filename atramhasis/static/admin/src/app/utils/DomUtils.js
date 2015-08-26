/**
 * utils Module for dom realted opertions
 * @module utils/DomUtils
 */
define([
  'dojo/_base/array',
  'dojo/dom-construct',
  'dojo/_base/lang',
  'dojo/_base/connect'
], function (
  array,
  domConstruct,
  lang,
  connect
) {
  return{
    /**
     * Adds 'options' to a 'select'.
     * @param {Object} select The 'select' element
     * @param {Object} options Options object, format:
     *   {
     *     data: {array},
     *     idProperty: {string},
     *     labelProperty: {string}
     *   }
     */
    addOptionsToSelect: function (select, options){
      array.forEach(options.data, function (item) {
        domConstruct.place('<option value="' + item[options.idProperty] + '">' + item[options.labelProperty] + '</option>',
          select);
      });
    },

    /**
     * Get the selected'option' from a 'select'.
     * @param {Object} select The 'select' element
     * @returns {String} Value from the selected 'option'
     */
    getSelectedOption: function (select) {
      return select.options[select.selectedIndex].value;
    }

  }
});