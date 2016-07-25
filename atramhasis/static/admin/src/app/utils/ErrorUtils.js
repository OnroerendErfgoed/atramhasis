/**
 * utils Module voor het verwerken van errors
 * @module utils/ErrorUtils
 */
define([
  'dojo/_base/array',
  'dojo/json'
], function (
  array,
  json
) {
  return{
    /**
     * Geeft de geserialiseerde error terug.
     * @param {Object} error De http error
     * @returns {Object} het json error object met title en message
     */
    parseError: function (error) {
      var parsedError = {
        title: 'Er is een fout opgetreden',
        message: error
      };

      if (error.response && error.response.text) {

        try {
          var errorResponse = json.parse(error.response.text);
          if (errorResponse.errors && errorResponse.errors.length > 0) {
            parsedError.title = errorResponse.message ? errorResponse.message : parsedError.title;
            parsedError.message = '';
            array.forEach(errorResponse.errors, function (errorDetail) {
              //parsedError.message += '-' + errorDetail + '</br>';
              for (var key in errorDetail){
                parsedError.message += '- ' + key + ': ' + errorDetail[key] + '</br>';
              }
            });
          }
          else {
            parsedError.message = errorResponse.message ? errorResponse.message : '';
          }
        } catch (e) {
          console.error('Error trying to parse error object', e);
        }
      }
      return parsedError;
    }
  };
});