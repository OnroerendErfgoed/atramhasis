$(document).ready(function() {
    var searchUrl = window.location.search.substr(1);
    const params = searchUrl.split();

    if (params.findIndex(element => element === 'view_tree') > -1) {
      openTreeTab();
    }
  });
  
  function openTreeTab() {
    document.getElementById('tree-link').click();
  }