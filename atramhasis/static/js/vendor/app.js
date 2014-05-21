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
    $("#schemerootlink").attr("href",  baseurl + "/");
    $("#exportrdflink").attr("href",  baseurl + ".rdf");
    $("#exportttllink").attr("href",  baseurl + ".ttl");
}

function getUrlVar(key){
    var result = new RegExp(key + "=([^&]*)", "i").exec(window.location.search);
    return result && unescape(result[1]) || "";
}
