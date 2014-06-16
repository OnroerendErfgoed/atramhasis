(function () {
    // let the loader know where to look for packages
    var config = {
        baseUrl: './',
        packages: [
            'dojo',
            'dijit',
            'dojox',
            'app',
            'dgrid',
            'put-selector',
            'xstyle'
        ]
    };
    require(config, ['app']);
})();