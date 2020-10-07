/*jshint unused:false*/
var dojoConfig = {
	async: true,
	parseOnLoad: false,
	tlmSiblingOfDojo: false,
	isDebug: true,
	packages: [
		{ name: 'dojo', location: 'dojo' },
		{ name: 'dijit', location: 'dijit' },
		{ name: 'dgrid', location: 'dgrid' },
		{ name: 'dstore', location: 'dstore' },
		{ name: 'dGrowl', location: 'dGrowl' },
		{ name: 'app', location: '../src/app' } /*build setup - must remain last in row*/
	]
};
