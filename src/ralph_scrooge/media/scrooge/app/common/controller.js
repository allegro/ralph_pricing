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
	}])
	.controller('menuStatsAdapterCtrl', ['$scope', 'stats', function($scope, stats){
		$scope.selected = {};
		$scope.startDate = new Date();
		$scope.endDate = new Date();
		$scope.$watch('date', function(newValue) {
			var start = newValue ? newValue.start : false;
			if (start) {
				stats.menuStats['year']['change'] = start.getFullYear();
				stats.menuStats['month']['change'] = start.getMonth() + 1;
				stats.menuStats['day']['change'] = start.getDate();
				stats.refreshData();
			}
		});
		$scope.$watch('stats.dates', function(newValue) {
			//TODO: change in REST API - min date instead of list of dates
			if (newValue) {
				var min_year = Object.keys(newValue)[0];
				var min_month = Object.keys(newValue[min_year])[0];
				var min_day = Object.keys(newValue[min_year][min_month])[0];
				$scope.startDate = new Date(min_year, min_month, min_day);
			}
		});
	}]);
