'use strict';

var scrooge = angular.module('scrooge.controller.allocationadmin', []);

scrooge.controller('allocationAdminCtrl', ['$scope', '$routeParams', '$http', 'stats', 'REST_URLS', '$sce', function ($scope, $routeParams, $http, stats, REST_URLS, $sce) {
    if (typeof($routeParams.tab) !== 'undefined') {
        stats.changeTab($routeParams.tab);
    }
    stats.breadcrumbs = ['tab'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Allocations admin';
    }
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationAdminData();
    };

    $scope.stats.menuStats.subpage.change = 'allocationadmin';
    $scope.stats.refreshData();

    $scope.getTotal = function (extra_costs, cost_type) {
        var total = 0;

        if (typeof(extra_costs) !== 'undefined' && typeof(extra_costs) !== 'string') {
            extra_costs.forEach(function (obj) {
                if (typeof(obj[cost_type]) !== 'undefined') {
                    total = total + Number(obj[cost_type]);
                }
            });
        }
        return total;
    };
    $scope.addRow = function (costList) {
        costList.push({'service': false, 'env': false, 'cost': 0, 'forecast_cost': 0, '_empty': true});
    };
    $scope.removeRow = function (index, currentList) {
        currentList.splice(index, 1);
    };

    $scope.uploadErrors = [];
    $scope.uploadInfo = $sce.trustAsHtml(`
        <strong>Accepted headers:</strong>
        <br />service_env_id;cost[;forecast_cost*]
        <br />service_uid;environment;cost[;forecast_cost*]
        <br />service_name;environment;cost[;forecast_cost*]
        <br />* - forecast_cost is optional
    `);

    $scope.onUpload = function(extraCostType) {
        $scope.extraCostType = extraCostType;
        $('#upload_modal').modal('show');
    };

    $scope.uploadFile = function() {
        $scope.uploadErrors = [];
        var urlAdminChunks = [REST_URLS.ALLOCATION_ADMIN]
        urlAdminChunks.push(stats.menuStats['year']['current']);
        urlAdminChunks.push(stats.menuStats['month']['current']);
        urlAdminChunks.push('extracosts/save/');

        var uploadUrl = urlAdminChunks.join('/');
        var file = $scope.myFile;
        if (file) {
            var fd = new FormData();
            fd.append('file', file);
            fd.append('extra_cost_type_id', $scope.extraCostType);
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
}]);
