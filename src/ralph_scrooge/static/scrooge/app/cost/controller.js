'use strict';

var scrooge = angular.module('scrooge.controller.cost', []);

scrooge.controller('costCtrl', ['$scope', '$routeParams', 'menuService', 'stats',  function ($scope, $routeParams, menuService, stats) {
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
        $scope.days = stats.cost.days;
        if (typeof(stats.cost.content) != 'undefined') {
            if (stats.cost.content != $scope.content) {
                $scope.content = stats.cost.content;
                stats.cost.content.forEach(function (element, key) {
                    $scope.$evalAsync(function() {
                        $('#table_' + key + ' table').bootstrapTable({
                            data: element.value,
                        });
                    });
                });
            }
        }
    });
}]);
