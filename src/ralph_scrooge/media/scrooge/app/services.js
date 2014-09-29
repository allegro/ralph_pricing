var ang_services = angular.module('ang_services', ['ngResource']);

ang_services.factory('stats', ['$http', function ($http) {
    return {
        components: {
            menuReady: false,
            contentReady: false,
            "months": [
                {"asString": "january", "asInt": 1, "intAsString": "01"},
                {"asString": "february", "asInt": 2, "intAsString": "02"},
                {"asString": "march", "asInt": 3, "intAsString": "03"},
                {"asString": "april", "asInt": 4, "intAsString": "04"},
                {"asString": "may", "asInt": 5, "intAsString": "05"},
                {"asString": "june", "asInt": 6, "intAsString": "06"},
                {"asString": "july", "asInt": 7, "intAsString": "07"},
                {"asString": "august", "asInt": 8, "intAsString": "08"},
                {"asString": "september", "asInt": 9, "intAsString": "09"},
                {"asString": "october", "asInt": 10, "intAsString": "10"},
                {"asString": "november", "asInt": 11, "intAsString": "11"},
                {"asString": "december", "asInt": 12, "intAsString": "12"}
            ],
            "menuStats": {
                "service": {"current": false, "change": false},
                "env": {"current": false, "change": false},
                "year": {"current": false, "change": false},
                "month": {"current": false, "change": false},
                "day": {"current": false, "change": false}
            },
        },
        init: function() {
            self = this
            $http({method: 'GET', url: '/scrooge/leftmenu/components/'}).
                success(function(data, status, headers, config) {
                    Object.keys(data['menuStats']).forEach(function (key){
                        self.components['menuStats'][key] = data['menuStats'][key]
                    })
                    self.components["menu"] = data["menu"]
                    self.components["dates"] = data["dates"]
                    self.refreshData()
                }).
                error(function(data, status, headers, config) {
                    // called asynchronously if an error occurs
                    // or server returns response with an error status.
                });
        },
        isLeapYear: function (year) {
            return ((year % 4 === 0) && (year % 100 !== 0)) || (year % 400 === 0);
        },
        daysInMonth: function (date) {
            return [31, (this.isLeapYear(date.getYear()) ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        },
        getDays: function() {
            self = this
            this.components['months'].forEach(function (month) {
                if (month.asString == self.components.menuStats.month.current) {
                    endDay = self.daysInMonth(new Date('2015', month.asInt-1))
                    var days = []
                    for (var i=1; i<=endDay[month.asInt-1]; i++) {
                        days.push(i)
                    }
                    self.components.days = days
                }
            })
        },
        refreshData: function() {
            self = this
            force = false
            refresh = false
            Object.keys(self.components['menuStats']).forEach(function (menu) {
                if (self.components.menuStats[menu]['current'] != self.components.menuStats[menu]['change']) {
                    refresh = true
                    self.components.menuStats[menu]['current'] = self.components.menuStats[menu]['change']
                }
                if (self.components.menuStats[menu]['change'] == false) {
                    force = true
                }
            })
            if (force == false && refresh == true) {
                $http({
                    method: 'GET',
                    url: '/scrooge/components/'
                        + self.components.menuStats['service']['current'] + '/'
                        + self.components.menuStats['env']['current'] + '/'
                        + self.components.menuStats['year']['current'] + '/'
                        + self.components.menuStats['month']['current'] + '/'
                        + self.components.menuStats['day']['current'],
                }).
                success(function(data, status, headers, config) {
                    self.components.content = data
                    self.components.currentContent = data[0]
                    console.log(self.components.content)
                }).
                error(function(data, status, headers, config) {
                    // called asynchronously if an error occurs
                    // or server returns response with an error status.
                });
            }
            if (self.components.menuReady == false) {
                self.components.menuReady = true
            }
        },
        inArray: function(value, array) {
            for (i in array) {
                if (array[i] == value) {
                    return true
                }
            }
            return false
        }
    }
}]);

ang_services.factory('menuService', ['stats', '$http', function (stats, $http) {
    return {
        test: [{"name": "Service #1"}, {"name": "Service #2"}],
        getLeftMenu: function(params) {
            return stats.components.menu
        },
        changeService: function(service) {
            stats.components.menuStats['service']['change'] = service
            stats.refreshData()
        },
        changeEnv: function(service, env) {
            stats.components.menuStats['env']['change'] = env
            stats.refreshData()
        },
    }
}]);

ang_services.factory('menuCalendar', ['stats', function (stats) {
    return {
        getYears: function() {
            years = []
            Object.keys(self.components['dates']).forEach(function (year) {
                years.push(year)
            })
            return years
        },
        getMonths: function() {
            months = []
            var current_year = self.components.menuStats['year']['current']
            Object.keys(self.components['dates'][current_year]).forEach(function (month) {
                months.push(month)
            })
            return months
        },
        getDays: function() {
            days = []
            var current_year = self.components.menuStats['year']['current']
            var current_month = self.components.menuStats['month']['current']
            self.components['dates'][current_year][current_month].forEach(function (day) {
                days.push(day)
            })
            return days
        },
        changeYear: function(year) {
            stats.components.menuStats['year']['change'] = year
            stats.refreshData()
        },
        changeDay: function(day) {
            stats.components.menuStats['day']['change'] = day
            stats.refreshData()
        },
        changeMonth: function(month) {
            stats.components.menuStats['month']['change'] = month
            var current_year = stats.components.menuStats['year']['current']
            var current_day = stats.components.menuStats['day']['current']
            if (stats.inArray(current_day, self.components['dates'][current_year][month]) == false) {
                days = self.components['dates'][current_year][month]
                stats.components.menuStats['day']['change'] = days[days.length-1]
            }
            stats.refreshData()
        },
    }
}]);
