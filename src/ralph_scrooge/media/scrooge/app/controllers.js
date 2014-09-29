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
        $scope.content = stats.components.content
        $scope.currentData = stats.components.currentContent
    });

    $scope.checkAll = function (modelName, checked) {
        angular.forEach($scope[modelName], function (item) {
            item.Selected = checked;
        });
    };
    $scope.preMonths = ['january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december']
    $scope.preventClose = function(event) { event.stopPropagation()};
    $scope.changeCategory = function(category_name) {
        $scope.content.forEach(function (category_type) {
            if (category_name = category_type.name) {
                console.log(category_name, category_type.name)
                $scope.currentData = category_type
            }
        })
    }
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
