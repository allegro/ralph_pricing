'use strict';

var scrooge = angular.module('scrooge.controller.allocationclient', []);

scrooge.controller('allocationClientCtrl', ['$scope', '$routeParams', '$http', 'menuService', 'menuCalendar', 'stats', function ($scope, $routeParams, $http, menuService, menuCalendar, stats) {
    stats.breadcrumbs = ['service', 'env', 'tab'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Allocations';
    }
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationClientData();
    };



    $scope.addRow = function (costList) {
        costList.push({'service': false, 'value': 0});
    };
    $scope.removeRow = function (index, currentList) {
        if (currentList.length >=2) {
            currentList.splice(index, 1);
        }
    };
    $scope.updateTotal = function (tab) {
        var _updateTotal = function (obj) {
            var count = 0;
            obj.rows.forEach(function (element) {
                count += parseFloat(element.value);
            });
            obj.total = count;
        };
        switch(tab) {
            case 'serviceDivision':
                _updateTotal(stats.allocationclient.serviceDivision);
                break;
            case 'serviceExtraCost':
                _updateTotal(stats.allocationclient.serviceExtraCost);
                break;
            case 'teamDivision':
                _updateTotal(stats.allocationclient.teamDivision);
                break;
            default:
                break;
        }
    };
    $scope.changeTab = function (tab) {
        stats.currentTab = tab;
    };
    $scope.changeTeam = function (team) {
        if (stats.menuStats.team.current != team.team) {
            stats.menuStats.team.change = team.id;
            stats.refreshData();
        }
    };





    $scope.stats.menuStats.subpage.change = 'allocationclient';
    $scope.stats.refreshData();
}]);
