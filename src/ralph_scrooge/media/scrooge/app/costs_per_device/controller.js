'use strict';

var scrooge = angular.module('scrooge.controller.costs_per_device', []);

scrooge.controller('costPerDeviceCtrl', ['$scope', 'stats',  function ($scope, stats) {
    // Base configuration
    stats.breadcrumbs = ['service', 'env'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Costs per device';
    }
}]);
