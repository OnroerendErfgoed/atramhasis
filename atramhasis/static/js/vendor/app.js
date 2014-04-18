$(document).ready(function () {
    /*
    *  Set form action for label search form
    */
    $('#search-form').submit(function(){
        var url = $("#scheme").val();
        $("#search-form").attr("action", url);
    });

    /*
    * Language cookie
    */
    var usrLang = $.cookie( '_LOCALE_' );
    if (usrLang==null)usrLang='en'
    $('#LanguageDropDownList').val(usrLang);
    $('#LanguageDropDownList').change(function () {
        changeLanguage($('#LanguageDropDownList').val());
    });
});

function changeLanguage(usrLang) {
    $.cookie('_LOCALE_', usrLang, { expires: 365, path: '/' });
    location.reload();
}

