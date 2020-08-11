$(document).ready(function() {
    var searchUrl = window.location.search.substr(1);
    const params = searchUrl.split('&');

    if(params[1] === 'view_tree') {
      openTreeTab();
      window.history.pushState('', null, window.location.href.split('?')[0]);
    }
  });
  
  function openTreeTab() {
    document.getElementById('tree-link').click()
  }