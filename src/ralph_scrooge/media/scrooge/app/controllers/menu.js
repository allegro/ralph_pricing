var scrooge = angular.module('scrooge.controllers', ['scrooge.services']);

scrooge.controller('SubMenuCtrl', ['$scope', '$location', 'SubMenu', function ($scope, $location, SubMenu) {
    $scope.stats.subMenus = SubMenu.items.get();
    $scope.stats.subMenus.$promise.then(function (subMenus) {
        $scope.stats.currentSubMenu = subMenus[0]
    })
    $scope.setActive = function(obj) {
        $scope.stats.currentSubMenu = obj
        if ($scope.stats.inArray($scope.stats.currentLeftMenu, $scope.stats.currentSubMenu.leftMenu) == false) {
            $scope.stats.currentLeftMenu = $scope.stats.getFirstExistMenu()
        }
    }
}]);
