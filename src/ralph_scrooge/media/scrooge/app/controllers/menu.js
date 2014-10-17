var scrooge = angular.module('scrooge.controllers', ['scrooge.services']);

scrooge.controller('MainMenuCtrl', ['$scope', '$location', 'MainMenu', function ($scope, $location, MainMenu){
    $scope.items = MainMenu.items.get();
    $scope.setActive = function(obj){
        $scope.active_url = obj.href;
        $scope.url = '#' + $location.url();
    }

    $scope.isActive = function(obj){
        return '#' + $location.url() == obj.href;
    }
}]);
