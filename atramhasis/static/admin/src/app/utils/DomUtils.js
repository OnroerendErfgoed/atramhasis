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
    addOptionsToSelect: function (select, options) {
      domConstruct.empty(select);
      if (options.placeholder) {
        domConstruct.place('<option value="">' + options.placeholder + '</option>', select);
      }
      array.forEach(options.data, function (item) {
        var itemProp = options.showId ? item[options.labelProperty] + ' (' + item[options.idProperty] + ')' :
          item[options.labelProperty];
        domConstruct.place('<option value="' + item[options.idProperty] + '">' + itemProp + '</option>', select);
      });
    },

    /**
     * Get the selected'option' from a 'select'.
     * @param {Object} select The 'select' element
     * @returns {String} Value from the selected 'option'
     */
    getSelectedOption: function (select) {
      if(select.options[select.selectedIndex]) {
        return select.options[select.selectedIndex].value;
      }
      else { return null; }
    }

  }
});