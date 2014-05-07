$(document).ready(function () {
    /*
    *  Set form action for label search form
    *  Set href for scheme browse link
    */
    $("#schemerootlink").attr("href",  $("#scheme").val() + "/");
    $("#search-form").attr("action", $("#scheme").val());

    $("#scheme").change(function() {
        var url = $("#scheme").val();
        $("#search-form").attr("action", url);
        $("#schemerootlink").attr("href",  url + "/");
    });
});


