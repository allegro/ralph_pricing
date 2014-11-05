var ang_controllers = angular.module('ang_controllers', []);

ang_controllers.controller('componentsCtrl', ['$scope', '$routeParams', 'menuService', 'menuCalendar', 'stats',  function ($scope, $routeParams, menuService, menuCalendar, stats) {
    stats.breadcrumbs = ["service", "env"];
    if ($scope.stats.currentSubMenu == false) {
        $scope.stats.currentSubMenu = 'Components';
    };
    $scope.stats.refreshCurrentSubpage = function () {
        stats.getComponentsData();
    };
    $scope.stats.menuStats.subpage.change = 'components';
    $scope.stats.refreshData();

    $scope.$watch(function () {
        $scope.days = stats.components.days;
        if (typeof(stats.components.content) != 'undefined') {
            if (stats.components.content != $scope.content) {
                $scope.content = stats.components.content;
                stats.components.content.forEach(function (element, key) {
                    $scope.$evalAsync(function() {
                        $('#table_' + key + ' table').bootstrapTable({
                            data: element.value,
                        });
                    });
                });
            };
        };
    });
    $scope.checkAll = function (modelName, checked) {
        angular.forEach($scope[modelName], function (item) {
            item.Selected = checked;
        });
    };
    $scope.preMonths = ['january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'];
    $scope.preventClose = function(event) {event.stopPropagation()};
}]);

ang_controllers.controller('mainCtrl', ['$scope', '$routeParams', 'menuService', 'menuCalendar', 'stats', function ($scope, $routeParams, menuService, menuCalendar, stats) {
    stats.init();
    $scope.menuService = menuService;
    $scope.menuCalendar = menuCalendar;
    $scope.stats = stats;
    $scope.getDictLength = function (dict) {
        if (typeof(dict) == 'object') {
            return Object.keys(dict).length;
        };
    };
}]);

var ButtonsCtrl = function ($scope) {

};

ang_controllers.controller('allocationClientCtrl', ['$scope', '$routeParams', 'menuService', 'menuCalendar', '$http', 'stats', function ($scope, $routeParams, $http, menuService, menuCalendar, stats) {
    stats.breadcrumbs = ["service", "env", "tab"];
    if ($scope.stats.currentSubMenu == false) {
        $scope.stats.currentSubMenu = 'Allocations';
    };
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationClientData();
    };
    $scope.stats.menuStats.subpage.change = 'allocationclient';
    $scope.stats.refreshData();

    $scope.addRow = function (costList) {
        costList.push({"service": false, "value": 0});
    };
    $scope.removeRow = function (index, currentList) {
        if (currentList.length >=2) {
            currentList.splice(index, 1);
        };
    };
    $scope.updateTotal = function (tab) {
        var _updateTotal = function (scope) {
            count = 0;
            save = true;
            scope.rows.forEach(function (element) {
                count += parseInt(element.value);
                if (element.service == false || element.env == false) {
                    save = false;
                };
            });
            scope.total = count;
        }
        switch(tab) {
            case 'serviceDivision':
                _updateTotal(stats.allocationclient.serviceDivision);
                break;
            case 'teamDivision':
                _updateTotal(stats.allocationclient.teamDivision);
                break;
            default:
                break;
        }
    };
    $scope.changeTab = function (tab) {
        stats.currentTab = tab;
    };
    $scope.changeTeam = function (team) {
        if (stats.menuStats.team.current != team.team) {
            stats.menuStats.team.change = team.id;
            stats.refreshData();
        };
    };
}]);

ang_controllers.controller('allocationAdminCtrl', ['$scope', '$routeParams', '$http', 'stats', function ($scope, $routeParams, $http, stats) {
    stats.breadcrumbs = ["tab"];
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationAdminData();
    };
    if ($scope.stats.currentSubMenu == false) {
        $scope.stats.currentSubMenu = 'Allocations Admin';
    };
    $scope.stats.menuStats.subpage.change = 'allocationadmin';
    $scope.stats.refreshData();
}]);
