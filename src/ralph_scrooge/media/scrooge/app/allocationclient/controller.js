'use strict';

var scrooge = angular.module('scrooge.controller.allocationclient', []);

scrooge.controller('allocationClientCtrl', ['$scope', '$routeParams', '$http', 'menuService', 'stats', 'REST_URLS', function ($scope, $routeParams, $http, menuService, stats, REST_URLS) {
    // Base configuration
    if (typeof($routeParams.tab) !== 'undefined') {
        stats.changeTab($routeParams.tab);
    }
    stats.breadcrumbs = ['tab', 'service', 'env'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Allocations';
    }
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationClientData();
    };
    $scope.stats.menuStats.subpage.change = 'allocationclient';
    $scope.stats.refreshData();

    /**
     * Add new row to given list.
     * @param {list} costList - List of dicts with row data.
     */
    $scope.addRow = function (costList) {
        costList.push({'service': false, 'value': 0, '_empty': true});
    };
    $scope.uploadErrors = [];

    $scope.onUpload = function() {
        $('#upload_modal').modal('show');
    };

    $scope.uploadFile = function() {
        $scope.uploadErrors = [];
        var urlClientChunks = [REST_URLS.ALLOCATION_CLIENT]
        if (stats.currentTab == 'teamDivision') {
            urlClientChunks.push(stats.menuStats['team']['current']);
            urlClientChunks.push(stats.menuStats['year']['current']);
            urlClientChunks.push(stats.menuStats['month']['current']);
            urlClientChunks.push('teamdivision/save/');
        } else {
            urlClientChunks.push(stats.menuStats['service']['current']);
            urlClientChunks.push(stats.menuStats['env']['current']);
            urlClientChunks.push(stats.menuStats['year']['current']);
            urlClientChunks.push(stats.menuStats['month']['current']);
            urlClientChunks.push('servicedivision/save/');
        }

        var uploadUrl = urlClientChunks.join('/');
        var file = $scope.myFile;
        if (file) {
            var fd = new FormData();
            fd.append('file', file);
            $http.post(uploadUrl, fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            }).success(function(data) {
                if (data['status'] == true) {
                    $('#upload_modal').modal('hide');
                    stats.refreshCurrentSubpage();
                } else {
                    $scope.uploadErrors = data['errors'];
                }
            }).error(function(){});
        }
    };

    /**
     * Remove row from given list.
     * @param {number} index - Element index to delete.
     * @param {list} currentList - List of dicts with row data.
     */
    $scope.removeRow = function (index, currentList) {
        currentList.splice(index, 1);
    };

    /**
     * Return sum of values for given tab.
     * @param {string} tab - Name of tab.
     */
    $scope.getTotal = function (tab) {
        var rows_with_data = stats.currentTabs[tab];
        if (typeof rows_with_data !== 'undefined') {
            var count = 0;
            rows_with_data.rows.forEach(function (element) {
                count += Number(element.value, 10);
            });
            return isNaN(count) ? 0.00 : count.toFixed(2);
        }
        return 0.00;
    };

    /**
     * Change tab.
     * @param {string} tab - Name of tab.
     */
    $scope.changeTab = function (tab) {
        stats.currentTab = tab;
    };
}]);
