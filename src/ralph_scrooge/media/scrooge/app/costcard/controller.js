'use strict';

var scrooge = angular.module('scrooge.controller.costcard', []);

scrooge.controller('costCardCtrl', ['$scope', '$routeParams', 'menuService', 'stats',  function ($scope, $routeParams, menuService, stats) {    // Base configuration
    stats.breadcrumbs = ['service', 'env'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Cost card';
    }
    $scope.stats.refreshCurrentSubpage = function () {
        stats.getCostCardData();
    };
    $scope.stats.menuStats.subpage.change = 'costcard';
    $scope.stats.refreshData();

    /**
     * Watchers. Render bootstrap-table component when there are new data.
     */
    $scope.$watch('stats.costcard.content', function () {
        if (stats.costcard.content) {
            /**
             * Some kind of hack for force refresh doom element,
             * it is using for refresh bootstrap-table table.
             */
            $scope.forceRefreshDomElement = [[]];
            $scope.$evalAsync(function() {
                $('#table-costcard table').bootstrapTable({
                    data: stats.costcard.content,
                });
            });
        }
    });

}]);
