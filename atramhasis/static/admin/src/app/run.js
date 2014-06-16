(function () {
    // let the loader know where to look for packages
    var config = {
        baseUrl: 'http://localhost:6543/static/admin/src/',
        packages: [
            'dojo',
            'dijit',
            'dojox',
            'dgrid',
            'put-selector',
            'xstyle',
            { name: 'app', location: 'app', map: {} },
        ]
    };
    require(config, ['app']);
})();