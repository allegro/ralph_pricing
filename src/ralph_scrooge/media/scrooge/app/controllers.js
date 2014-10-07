var ang_controllers = angular.module('ang_controllers', []);

ang_controllers.controller('components', ['$scope', '$routeParams','menuService', 'menuCalendar', 'stats',  function ($scope, $routeParams, menuService, menuCalendar, stats) {
    stats.init()
    $scope.menuService = menuService
    $scope.menuCalendar = menuCalendar
    $scope.stats = stats

    stats.getDays()
    $scope.days = stats.components.days
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

ang_controllers.controller('mainCtrl', ['$scope', '$routeParams', 'stats', function ($scope, $routeParams, stats) {

}]);

ang_controllers.controller('componentsContentCtrl', ['$scope', '$routeParams', '$http', 'stats', function ($scope, $routeParams, $http, stats) {
    $scope.content = stats.components.content
    $scope.currentData = stats.components.currentContent
    $scope.$watch(function () {
        $scope.content = stats.components.content
        $scope.currentData = stats.components.currentContent
    });
}]);

var ButtonsCtrl = function ($scope) {

};
