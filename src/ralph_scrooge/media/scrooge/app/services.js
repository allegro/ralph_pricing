var ang_services = angular.module('ang_services', ['ngResource']);

ang_services.factory('stats', ['$http', function ($http) {
    return {
        months: [
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
	    menuStats: {
	        "service": {"current": false, "change": false},
	        "env": {"current": false, "change": false},
	        "month": {"current": false, "change": false},
	        "day": {"current": false, "change": false}
	    },
	    menu: {
	        "Stash": {
	            "envs": [{"env": "prod", "show": true}, {"env": "dev"}, {"env": "test"}],
	            "show": true,
	        },
	        "Allegro": {
	            "envs": [{"env": "prod"}, {"env": "dev"}, {"env": "test"}],
	        },
	        "Agito": {
	            "envs": [{"env": "dev"}],
	        }
	    },
        isLeapYear: function (year) {
            return ((year % 4 === 0) && (year % 100 !== 0)) || (year % 400 === 0);
        },
        daysInMonth: function (date) {
            return [31, (this.isLeapYear(date.getYear()) ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        },
        getDays: function() {
            self = this
            this.months.forEach(function (month) {
                if (month.asString == self.menuStats.month.current) {
                    endDay = self.daysInMonth(new Date('2015', month.asInt-1))
                    var days = []
                    for (var i=1; i<=endDay[month.asInt-1]; i++) {
                        days.push(i)
                    }
                    self.days = days
                }
            })
        },
        refreshData: function() {
            self = this
            force = false
            refresh = false
            Object.keys(self.menuStats).forEach(function (menu) {
                if (self.menuStats[menu]['current'] != self.menuStats[menu]['change']) {
                    refresh = true
                    self.menuStats[menu]['current'] = self.menuStats[menu]['change']
                }
                if (self.menuStats[menu]['change'] == false) {
                    force = true
                }
            })

            if (force == false && refresh == true) {
                console.log("New Data!")
            }
        }
    }
}]);

ang_services.factory('menuService', ['$http', 'stats', function ($http, stats) {
    return {
    	init: function() {
    		//Getting and prepare data
    	},
        getLeftMenu: function(params) {
        	return stats.menu
        },
        changeService: function(service) {
            Object.keys(stats.menu).forEach(function (scopeService) {
        		stats.menu[scopeService]['show'] = false
            })
    		stats.menu[service]['show'] = true
    		stats.menuStats['service']['change'] = service
        },
        changeEnv: function(service, env) {
            Object.keys(stats.menu).forEach(function (scopeService) {
        		stats.menu[scopeService]['envs'].forEach(function (envScope) {
	        		if (env.env == envScope.env && scopeService == service) {
	        			envScope.show = true;
	        		} else {
	        			envScope.show = false;
	        		}
           		});
        	});
        	stats.menuStats['env']['change'] = env.env
        	stats.refreshData()
        },
        checkActiveService: function(service) {
        	return stats.menu[service]['show']
        },
        checkActiveEnv: function(service, env) {
        	return_value = false
        	test = stats.menu[service]['envs'].forEach(function (envScope) {
        		if (env.env == envScope.env) {
        			if (envScope.show == true) {
        				return_value = true
        			}
        		}
        	})
        	return return_value
        },
    }
}]);

ang_services.factory('menuCalendar', ['$http', 'stats', function ($http, stats) {
    return {
    	init: function() {
    		//Getting and prepare data
    	},
        checkCurrentMonth: function (month) {
            if (stats.menuStats['month']['current'] == month.asString) {
                return true
            } else {
                return false
            }
        },
        checkCurrentDay: function (day) {
            if (stats.menuStats['day']['current'] == day) {
                return true
            } else {
                return false
            }
        },
        getMonths: function() {
            this.getDays()
            return stats.months
        },
        getDays: function() {
            stats.getDays()
        },
        changeDay: function(day) {
            stats.menuStats['day']['change'] = day
        	stats.refreshData()
        },
        changeMonth: function(month) {
            stats.months.forEach(function (scopeMonth) {
                if (scopeMonth.asString == month.asString) {
                    scopeMonth.active = true
                } else {
                    scopeMonth.active = false
                }
            })
    		stats.menuStats['month']['change'] = month.asString
        	stats.refreshData()
        },
    }
}]);
