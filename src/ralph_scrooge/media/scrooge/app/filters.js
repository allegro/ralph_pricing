var ang_filters = angular.module('ang_filters', []);

ang_filters.filter('intToMonth', function() {
    var _intToMonth = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December'
    };
    return function(input, scope) {
        return _intToMonth[input];
    };
});

ang_filters.filter('breadcrumbs', ['stats', function(stats) {
    return function(input, scope, asd) {
        switch(scope) {
            case 'env':
                for (var i in stats.leftMenus[stats.currentLeftMenu]) {
                    for (var k in stats.leftMenus[stats.currentLeftMenu][i].value.envs) {
                        if (stats.leftMenus[stats.currentLeftMenu][i].value.envs[k].id == input) {
                            return stats.leftMenus[stats.currentLeftMenu][i].value.envs[k].name;
                        };
                    };
                };
                break;
            case 'service':
                for (var i in stats.leftMenus[stats.currentLeftMenu]) {
                    if (stats.leftMenus[stats.currentLeftMenu][i].id == input) {
                        return stats.leftMenus[stats.currentLeftMenu][i].name;
                    };
                };
                break;
            default:
                return false;
                break;
        };
    };
}]);
