'use strict';

var scrooge = angular.module('scrooge.controller.component', []);

scrooge.controller('componentsCtrl', ['$scope', '$routeParams', 'menuService', 'stats',  function ($scope, $routeParams, menuService, stats) {
    stats.breadcrumbs = ['service', 'env'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Components';
    }
    $scope.stats.refreshCurrentSubpage = function () {
        stats.getComponentsData();
    };
    $scope.stats.menuStats.subpage.change = 'components';
    $scope.stats.refreshData();

    $scope.$watch('stats.components.content', function () {
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
            }
        }
    });
    $scope.checkAll = function (modelName, checked) {
        angular.forEach($scope[modelName], function (item) {
            item.Selected = checked;
        });
    };
    $scope.preMonths = ['january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'];
    $scope.preventClose = function(event) {event.stopPropagation();};
}]);
