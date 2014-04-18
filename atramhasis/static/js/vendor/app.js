$(document).ready(function () {
    /*
    *  Set form action for label search form
    */
    $('#search-form').submit(function(){
        var scheme = $("#scheme").val();
        $("#search-form").attr("action", '/conceptschemes/' + scheme + '/c');
    });
});