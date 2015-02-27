'use strict';

var scrooge = angular.module('scrooge.controller.cost', []);

scrooge.controller('costCtrl', ['$scope', '$routeParams', 'menuService', 'menuCalendar', 'stats',  function ($scope, $routeParams, menuService, menuCalendar, stats) {
    stats.breadcrumbs = ['service', 'env'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Costs';
    }
    $scope.stats.refreshCurrentSubpage = function () {
        stats.getCostData();
    };
    $scope.stats.menuStats.subpage.change = 'costs';
    $scope.stats.refreshData();

    $scope.$watch('stats.cost.content', function () {
        if (typeof(stats.cost.content) != 'undefined' && stats.cost.content.length !== 0) {
            $scope.$evalAsync(function() {
                $('#table_cost').bootstrapTable({
                    data: stats.cost.content.value,
                });
            });
        }
    });
}]);
