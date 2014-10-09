var ang_controllers = angular.module('ang_controllers', []);

ang_controllers.controller('componentsCtrl', ['$scope', '$routeParams', 'menuService', 'menuCalendar', 'stats',  function ($scope, $routeParams, menuService, menuCalendar, stats) {
    stats.refreshCurrentSubpage = function () {
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

    stats.getDays()
    $scope.days = stats.components.days
    $scope.getDictLength = function (dict) {
        return Object.keys(dict).length
    }
}]);


var ButtonsCtrl = function ($scope) {

};

ang_controllers.controller('allocationClientCtrl', ['$scope', '$routeParams', 'menuService', 'menuCalendar', '$http', 'stats', function ($scope, $routeParams, $http, menuService, menuCalendar, stats) {
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationClientData()
    }
    $scope.addRow = function (costList) {
        costList.push(
            {"service": false, "value": 0}
        )
    }
    $scope.removeRow = function (index, costList) {
        costList.splice(index, 1);
    }
    $scope.updateTotal = function (tab) {
        switch(tab) {
            case 'serviceDivision':
                count = 0
                save = true
                stats.allocationclient.serviceDivision.rows.forEach(function (element) {
                    count += parseInt(element.value)
                    if (element.service == false || element.env == false) {
                        save = false
                    }
                })
                stats.allocationclient.serviceDivision.total = count
                if (stats.allocationclient.serviceDivision.total == 100 && save) {
                    stats.saveAllocation(tab)
                }
                break;
            case 'serviceExtraCost':
                break;
            case 'teamDivision':
                break;
            default:

        }
    }
}]);
