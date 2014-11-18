'use strict';

var scrooge = angular.module('scrooge.service.menu', ['ngResource']);

scrooge.factory('SubMenu', ['$resource', function ($resource) {
    return {
        'items': $resource('/scrooge/rest/submenu', {}, {
            get: {
                method: 'GET',
                cache: true,
                isArray: true,
            }
        })
    };
}]);

scrooge.factory('menuService', ['stats', function (stats) {
    return {
        changeService: function(service) {
            stats.menuStats['service']['change'] = service.id;
            var envExist = false;
            service.value.envs.forEach(function(element) {
                if (element.env == stats.menuStats['env']['current']) {
                    envExist = true;
                }
            });
            if (envExist === false) {
                stats.menuStats['env']['change'] = service.value.envs[0].id;
            }
            stats.refreshData();
        },
        changeEnv: function(env) {
            stats.menuStats['env']['change'] = env;
            stats.refreshData();
        },
    };
}]);

scrooge.factory('menuCalendar', ['stats', function (stats) {
    return {
        getYears: function() {
            var years = [];
            if (typeof(self.dates) != 'undefined') {
                Object.keys(self.dates).forEach(function (year) {
                    years.push(year);
                });
            }
            return years;
        },
        getMonths: function() {
            var months = [];
            if (typeof(self.dates) != 'undefined') {
                var current_year = self.menuStats['year']['current'];
                Object.keys(self.dates[current_year]).forEach(function (month) {
                    months.push(month);
                });
            }
            return months;
        },
        getDays: function() {
            var days = [];
            if (typeof(self.dates) != 'undefined') {
                var current_year = self.menuStats['year']['current'];
                var current_month = self.menuStats['month']['current'];
                self.dates[current_year][current_month].forEach(function (day) {
                    days.push(day);
                });
            }
            return days;
        },
        changeYear: function(year) {
            stats.menuStats['year']['change'] = year;
            stats.refreshData();
        },
        changeDay: function(day) {
            stats.menuStats['day']['change'] = day;
            stats.refreshData();
        },
        changeMonth: function(month) {
            stats.menuStats['month']['change'] = month;
            var current_year = stats.menuStats['year']['current'];
            var current_day = stats.menuStats['day']['current'];
            if (stats.inArray(current_day, self.dates[current_year][month]) === false) {
                var days = self.dates[current_year][month];
                stats.menuStats['day']['change'] = days[days.length-1];
            }
            stats.refreshData();
        },
    };
}]);
