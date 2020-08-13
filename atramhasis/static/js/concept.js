$(document).ready(function () {
  var searchUrl = window.location.search.substr(1);
  var params = searchUrl.split();

  if (params.indexOf('view_tree') > -1) {
    openTreeTab();
  }
});

function openTreeTab() {
  document.getElementById('tree-link').click();
}