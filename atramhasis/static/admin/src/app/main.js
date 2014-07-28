define([
	'./App',
	'dojo/domReady!'
], function (
	App
) {
	'use strict';

    var app = window.app = {};

	app.main = new App().placeAt("appDiv");

	app.main.startup();
});
