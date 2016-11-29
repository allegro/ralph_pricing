'use strict';

var scrooge = angular.module('scrooge.controller.costcard', []);

scrooge.controller('costCardCtrl', ['$scope', '$routeParams', '$location', 'menuService', 'stats', 'SymbolServiceResolver', function ($scope, $routeParams, $location, menuService, stats, SymbolServiceResolver) {    // Base configuration
    stats.breadcrumbs = ['service', 'env'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Cost card';
    }
    if ($routeParams.uid != undefined) {
        var res = SymbolServiceResolver.get({id: $routeParams.uid}, function(data) {
            $location.path('/costcard/'+ data.id +'/');
        });
    }
    stats.init_promise.success(function() {
        if ($routeParams.service != undefined) {
            menuService.changeService(stats.services[parseInt($routeParams.service)]);
        }
        if ($routeParams.env != undefined) {
            menuService.changeEnv(stats.envs[parseInt($routeParams.env)].id);
        }
    })
    $scope.stats.refreshCurrentSubpage = function () {
        stats.getCostCardData();
    };
    $scope.stats.menuStats.subpage.change = 'costcard';

    /**
     * Watchers. Render bootstrap-table component when there are new data.
     */
    $scope.$watch('stats.costcard.content', function () {
        if (stats.costcard.content) {
            /**
             * Some kind of hack for force refresh dom element,
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
