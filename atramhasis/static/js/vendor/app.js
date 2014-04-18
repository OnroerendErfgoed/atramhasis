$(document).ready(function () {
    /*
    *  Set form action for label search form
    */
    $('#search-form').submit(function(){
        var url = $("#scheme").val();
        $("#search-form").attr("action", url);
    });
});