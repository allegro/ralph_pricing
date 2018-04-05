'use strict';

var scrooge = angular.module('scrooge.controller', []);

scrooge
	.controller('mainCtrl', ['$scope', '$routeParams', 'menuService', 'stats', function ($scope, $routeParams, menuService, stats) {
		stats.init();
		$scope.menuService = menuService;
		$scope.stats = stats;
		$scope.getDictLength = function (dict) {
			if (typeof(dict) == 'object') {
				return Object.keys(dict).length;
			}
		};
	}]);
