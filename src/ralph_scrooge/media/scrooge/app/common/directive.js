'use strict';

var scrooge = angular.module('scrooge.directive', []);

scrooge
	.directive('tabsdirective', function() {
	    return {
	        restrict: 'EACM',
	        templateUrl: '/static/scrooge/partials/tabs.html',
	        replace: true,
	    };
	})
	.directive('scCalendar', ['STATIC_URL', function(STATIC_URL) {
		var isLeapYear = function (year) {
			return ((year % 4 === 0) && (year % 100 !== 0)) || (year % 400 === 0);
		};

		var daysInMonth = function (year) {
			return [31, (isLeapYear(year) ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
		};

		var generateListOfIntegers = function(start, end) {
			var list = [];
			for (var i = parseInt(start); i <= parseInt(end); i++) {
				list.push(i);
			}
			return list;
		};

		return {
			scope: {
				selected: '=',
				view: '=',
				startDate: '=',
				endDate: '='
			},
			restrict: 'E',
			templateUrl: STATIC_URL + 'scrooge/partials/sc-calendar.html',
			link: function($scope) {
				var startDate = $scope.startDate;
				var endDate = $scope.endDate;
				var view_mapper = {
					yearly: 2,
					monthly: 1,
					daily: 0
				};

				$scope.date = {};
				$scope.date.year = endDate.getFullYear();
				$scope.date.month = endDate.getMonth() + 1;
				$scope.date.day = endDate.getDate();

				var refresh = function() {
					startDate = $scope.startDate;
					endDate = $scope.endDate;
					$scope.years = getYears(startDate, endDate);
					$scope.months = getMonths($scope.date.year);
					$scope.days = getDays($scope.date.year, $scope.date.month);
				};

				var getYears = function() {
					return generateListOfIntegers(startDate.getFullYear(), endDate.getFullYear());
				};

				var getMonths = function(year) {
					var start = 1;
					var end = 12;
					if (year === startDate.getFullYear()) {
						start = startDate.getMonth();
					}
					if (year === endDate.getFullYear()) {
						end = endDate.getMonth() + 1;
					}
					return generateListOfIntegers(start, end);
				};

				var getDays = function(year, month) {
					var start = 1;
					var end = daysInMonth(year)[month-1];
					if (year === startDate.getFullYear() && month === startDate.getMonth()) {
						start = startDate.getDate();
					}
					if (year === endDate.getFullYear() && month === endDate.getMonth() + 1) {
						end = endDate.getDate();
					}
					return generateListOfIntegers(start, end);
				};

				$scope.changeYear = function(year) {
					$scope.date.year = year;
					$scope.date.month = 0;
					$scope.date.day = 0;
					$scope.months = getMonths($scope.date.year);
					$scope.days = [];
				};

				$scope.changeMonth = function(month) {
					$scope.date.month = month;
					$scope.date.day = 0;
					$scope.days = getDays($scope.date.year, $scope.date.month);
				};
				$scope.changeDay = function(day) {
					$scope.date.day = day;
				};

				var watch_variable_mapper = {
					yearly: 'year',
					monthly: 'month',
					daily: 'day'
				};
				var watch_variable = watch_variable_mapper[$scope.view] || 'daily';

				$scope.$watch('view', function(newValue){
					$scope.showed = view_mapper[newValue];
					watch_variable = watch_variable_mapper[$scope.view];
				});

				$scope.$watch('startDate', function(){
					refresh();
				});

				$scope.$watch('endDate', function(){
					refresh();
				});

				$scope.$watch(function() {
					return $scope.date[watch_variable];
				}, function(newValue) {
					if (newValue) {
						refresh();
						var start = new Date(
							$scope.date.year, $scope.date.month - 1, $scope.date.day || 1
						);
						$scope.selected = {
							start: start,
							end: null
						};
					}
				});
				refresh();
			}
		};
	}])
	.directive('scDatepicker', ['STATIC_URL', function(STATIC_URL){
		// one-way binding, datepicker only return value
		return {
			scope: {
				view: '@',
				selected: '='
			},
			restrict: 'E',
			templateUrl: STATIC_URL + 'scrooge/partials/sc-datepicker.html',
			link: function($scope, element, attrs) {
				var view = $scope.view;
				var with_range = 'range' in attrs;
				var format = attrs['format'] || 'dd/mm/yyyy';
				$scope.range = with_range;
				var view_mapper = {
					yearly: 2,
					monthly: 1,
					daily: 0
				};
				var params = {
					startView: view_mapper[view],
					minViewMode: view_mapper[view],
					format: format,
					clearBtn: 'clear' in attrs,
					calendarWeeks: 'weeks' in attrs,
					autoclose: 'autoclose' in attrs,
					todayHighlight: 'today' in attrs,
				};
				var selector = with_range ? '.input-daterange' : '.input-single';
				var d = $(selector, element).datepicker(params);

				$scope.selected = {start: null, end: null};

				if (with_range) {
					$scope.$watch('date_range', function() {
						var start_date = $('.date-start', d).datepicker('getDate');
						var end_date = $('.date-end', d).datepicker('getDate');
						if (!isNaN(start_date)){
							$scope.selected.start = start_date;
						}
						if (!isNaN(end_date)){
							$scope.selected.end = end_date;
						}
					}, true);
				}
				else {
					$scope.$watch('date_single', function() {
						var date = d.datepicker('getDate');
						if (!isNaN(date)){
							$scope.selected.start = date;
							$scope.selected.end = null;
						}
					});
				}
				// TODO: two-way binding
			}
		};
	}]);
