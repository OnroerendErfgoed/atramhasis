// Foundation JavaScript
// Documentation can be found at: https://foundation.zurb.com/docs
$(document).foundation();

// Function that makes the mobile menu work.
$('#mobile-menu-select').change(function () {
  var selectedUrl = $(this).val();
  try {
    var parsedUrl = new URL(selectedUrl, window.location.origin);
    if (
      (parsedUrl.protocol === 'http:' || parsedUrl.protocol === 'https:') &&
      parsedUrl.origin === window.location.origin
    ) {
      window.location = parsedUrl.pathname + parsedUrl.search + parsedUrl.hash;
    }
  } catch (e) {
    // Ignore invalid URL values.
  }
});

$(document).ready(function () {
  /*
   *  Set form action for label search form
   *  Set href for scheme links
   *  On startup and value change
   */
  setSchemeUrls($('#scheme').val());

  $('#scheme').change(function () {
    var url = $('#scheme').val();
    setSchemeUrls(url);
  });
});

function setSchemeUrls(baseurl) {
  $('#search-form').attr('action', baseurl);
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getUrlVar(key) {
  var result = new RegExp(key + '=([^&]*)', 'i').exec(window.location.search);
  return (result && unescape(result[1])) || '';
}
