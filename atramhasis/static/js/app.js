// Foundation JavaScript
// Documentation can be found at: http://foundation.zurb.com/docs
$(document).foundation();

// Function that makes the mobile menu work.
$('#mobile-menu-select').change(function() {
  window.location = $(this).val();
});

$(document).ready(function () {
    /*
     *  Set form action for label search form
     *  Set href for scheme links
     *  On startup and value change
     */
  setSchemeUrls( $("#scheme").val());

  $("#scheme").change(function() {
    var url = $("#scheme").val();
    setSchemeUrls(url);
  });
});

function setSchemeUrls(baseurl){
  $("#search-form").attr("action", baseurl);
}

function getUrlVar(key){
  var result = new RegExp(key + "=([^&]*)", "i").exec(window.location.search);
  return result && unescape(result[1]) || "";
}

