'use strict';

var scrooge = angular.module('scrooge.controller.allocationadmin', []);

scrooge.controller('allocationAdminCtrl', ['$scope', '$routeParams', '$http', 'stats', function ($scope, $routeParams, $http, stats) {
    if (typeof($routeParams.tab) !== 'undefined') {
        stats.changeTab($routeParams.tab);
    }
    stats.breadcrumbs = ['tab'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Allocations Admin';
    }
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationAdminData();
    };
    $scope.stats.menuStats.subpage.change = 'allocationadmin';
    $scope.stats.refreshData();

    $scope.getTotal = function (extra_costs, cost_type) {
        var total = 0;

        if (typeof(extra_costs) !== 'undefined' && typeof(extra_costs) !== 'string') {
            extra_costs.forEach(function (obj) {
                if (typeof(obj[cost_type]) !== 'undefined') {
                    total = total + Number(obj[cost_type]);
                }
            });
        }
        return total;
    };
    $scope.addRow = function (costList) {
        costList.push({'service': false, 'env': false, 'cost': 0, 'forecast_cost': 0});
    };
    $scope.removeRow = function (index, currentList) {
        if (currentList.length >= 2) {
            currentList.splice(index, 1);
        }
    };
}]);
