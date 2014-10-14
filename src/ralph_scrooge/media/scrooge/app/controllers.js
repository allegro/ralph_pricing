var ang_controllers = angular.module('ang_controllers', []);

ang_controllers.controller('componentsCtrl', ['$scope', '$routeParams', 'menuService', 'menuCalendar', 'stats',  function ($scope, $routeParams, menuService, menuCalendar, stats) {
    $scope.stats.refreshCurrentSubpage = function () {
        stats.getComponentsData()
    }
    $scope.$watch(function () {
        $scope.days = stats.components.days
        if (typeof(stats.components.content) != 'undefined') {
            if (stats.components.content != $scope.content) {
                $scope.content = stats.components.content
                stats.components.content.forEach(function (element, key) {
                    $scope.$evalAsync(function() {
                        $('#table_' + key + ' table').bootstrapTable({
                            data: element.value,
                        });
                    });
                });
            }
        }
    });
    $scope.checkAll = function (modelName, checked) {
        angular.forEach($scope[modelName], function (item) {
            item.Selected = checked;
        });
    };
    $scope.preMonths = ['january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december']
    $scope.preventClose = function(event) {event.stopPropagation()};
}]);

ang_controllers.controller('mainCtrl', ['$scope', '$routeParams', 'menuService', 'menuCalendar', 'stats', function ($scope, $routeParams, menuService, menuCalendar, stats) {
    stats.init()
    $scope.menuService = menuService
    $scope.menuCalendar = menuCalendar
    $scope.stats = stats
    $scope.getDictLength = function (dict) {
        if (typeof(dict) == 'dict') {
            return Object.keys(dict).length
        }
    }
    $scope.$watch('stats.menuStats', function() { $scope.stats.refreshData() });
}]);


var ButtonsCtrl = function ($scope) {

};

ang_controllers.controller('allocationClientCtrl', ['$scope', '$routeParams', 'menuService', 'menuCalendar', '$http', 'stats', function ($scope, $routeParams, $http, menuService, menuCalendar, stats) {
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationClientData()
    }
    $scope.addRow = function (costList) {
        costList.push({"service": false, "value": 0})
    }
    $scope.removeRow = function (index, costList) {
        costList.splice(index, 1);
    }
    $scope.updateTotal = function (tab) {
        var _updateTotal = function (scope) {
            count = 0
            save = true
            scope.rows.forEach(function (element) {
                count += parseInt(element.value)
                if (element.service == false || element.env == false) {
                    save = false
                }
            })
            scope.total = count
        }
        switch(tab) {
            case 'serviceDivision':
                _updateTotal(stats.allocationclient.serviceDivision)
                break;
            case 'serviceExtraCost':
                break;
            case 'teamDivision':
                _updateTotal(stats.allocationclient.teamDivision)
                break;
            default:
                break;
        }
    }
    $scope.changeTab = function (tab) {
        stats.currentTab = tab
    }
    $scope.changeTeam = function (team) {
        if (stats.menuStats.team.current != team.team) {
            stats.menuStats.team.change = team.team
            stats.refreshData();
        }
    }
}]);
