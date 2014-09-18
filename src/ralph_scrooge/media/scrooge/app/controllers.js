var ang_controllers = angular.module('ang_controllers', []);

ang_controllers.controller('components', ['$scope', '$routeParams', function ($scope, $routeParams) {
    $scope.models = [{
        Name: "HP ProLiant DL 360 G6",
        Selected: true,
    }, {
        Name: "HP ProLiant BL2x220c G5",
        Selected: true,
    }, {
        Name: "HP ProLiant DL 360 G6",
        Selected: true,
    }, {
        Name: "IBM BladeCenter HS21",
        Selected: true,
    }, {
        Name: "HP ProLiant BL2x220c G5",
        Selected: true,
    }, {
        Name: "HP ProLiant BL2x220c G5",
        Selected: true,
    }, {
        Name: "IBM Ethernet SM (32R1866)",
        Selected: true,
    }];
    $scope.datacenters = [{
        Name: "DC2",
        Selected: true,
    }, {
        Name: "DC4",
        Selected: true,
    }];
    $scope.environments = [{
        Name: "Prod",
        Selected: true,
    }, {
        Name: "Dev",
        Selected: true,
    }, {
        Name: "Test",
        Selected: true,
    }];
    $scope.results = [{
    	id: 243,
    	name: 'HP ProLiant DL 360 G6',
    	sn: 'DA34FD1X0L',
    	barcode: '1046_CD'
    }, {
    	id: 43,
    	name: 'IBM BladeCenter HS21',
    	sn: 'AWCK89AD9',
    	barcode: '74516_A'
    }, {
    	id: 134,
    	name: 'IBM Ethernet SM (32R1866)',
    	sn: 'ADW891AD02',
    	barcode: '44213_F'
    }]
    $scope.checkAll = function (modelName, checked) {
        angular.forEach($scope[modelName], function (item) {
            item.Selected = checked;
        });

    };
    $scope.preventClose = function(event) { event.stopPropagation(); };
}]);

ang_controllers.controller('mainCtrl', ['$scope', '$routeParams', function ($scope, $routeParams) {

}]);

var ButtonsCtrl = function ($scope) {

};
