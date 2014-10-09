var ang_services = angular.module('ang_services', ['ngResource']);

ang_services.factory('stats', ['$http', function ($http) {
    return {
        menuActive: false,
        menuReady: false,
        menus: false,
        menuStats: {
            "service": {"current": false, "change": false},
            "env": {"current": false, "change": false},
            "year": {"current": false, "change": false},
            "month": {"current": false, "change": false},
            "day": {"current": false, "change": false},
        },
        components: {
            contentReady: 0,
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
            "contentStats": {
                "table": false,
            },
        },
        allocationclient: {
            allocationActiveTab: 'allocate_costs',
            contentReady: 0,
            serviceDivision: {
                rows: [{"service": false, "value": 0}]
            },
            serviceExtraCost: {
                rows: [{"service": false, "value": 0}]
            },
            teamDivision: {
                rows: [{"service": false, "value": 0}]
            }
        },
        init: function() {
            self = this
            $http({method: 'GET', url: '/scrooge/leftmenu/components/'}).
                success(function(data, status, headers, config) {
                    Object.keys(data['menuStats']).forEach(function (key){
                        self.menuStats[key] = data['menuStats'][key]
                    })
                    self.menus = data["menus"]
                    self.components["dates"] = data["dates"]
                    self.menuActive = Object.keys(self.menus)[0]
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
                if (month.asString == self.menuStats.month.current) {
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
                self.refreshCurrentSubpage()
            }
            if (self.menuReady == false) {
                self.menuReady = true
            }
        },
        refreshCurrentSubpage: function () {},
        inArray: function(value, array) {
            for (i in array) {
                if (array[i] == value) {
                    return true
                }
            }
            return false
        },
        getComponentsData: function () {
            self.components.contentReady += 1
            $http({
                method: 'GET',
                url: '/scrooge/components/'
                    + self.menuStats['service']['current'] + '/'
                    + self.menuStats['env']['current'] + '/'
                    + self.menuStats['year']['current'] + '/'
                    + self.menuStats['month']['current'] + '/'
                    + self.menuStats['day']['current'],
            }).
            success(function(data, status, headers, config) {
                self.components.content = data
                self.components.contentReady -= 1
                self.components.contentStats.table = data[0].name
            }).
            error(function(data, status, headers, config) {
                self.components.contentReady -= 1
            });
        },
        getAllocationClientData: function () {
            self.components.contentReady += 1
            $http({
                method: 'GET',
                url: '/scrooge/allocateclient/'
                    + self.menuStats['service']['current'] + '/'
                    + self.menuStats['env']['current'] + '/'
                    + self.menuStats['year']['current'] + '/'
                    + self.menuStats['month']['current'] + '/'
            }).
            success(function(data, status, headers, config) {
                self.components.content = data
                self.components.contentReady -= 1
                self.components.contentStats.table = data[0].name
            }).
            error(function(data, status, headers, config) {
                self.components.contentReady -= 1
            });
        },
        saveAllocation: function (tab) {
            switch(tab) {
                case 'serviceDivision':
                    url = '/scrooge/allocateclient/servicedivision/save/'
                    data = {
                        'service': self.menuStats['service']['current'],
                        'data': self.allocationclient.serviceDivision.rows,
                    }
                    break;
                case 'serviceExtraCost':
                    url = '/scrooge/allocateclient/servicedivision/save/'
                    data = {
                        'service': self.menuStats['service']['current'],
                        'data': self.allocationclient.serviceExtraCosts.rows,
                    }
                    break;
                case 'teamDivision':
                    url = '/scrooge/allocateclient/servicedivision/save/'
                    data = {
                        'service': self.menuStats['service']['current'],
                        'data': self.allocationclient.teamDivision.rows,
                    }
                    break;
                default:
                    url = ''
                    data = {}
            }
            $http({
                method: 'POST',
                url: url,
                data: {
                    'service': self.menuStats['service']['current'],
                    'data': data,
                }
            }).
            success(function(data, status, headers, config) {
                console.log(data)
            }).
            error(function(data, status, headers, config) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
            });
        }
    }
}]);

ang_services.factory('menuService', ['stats', '$http', function (stats, $http) {
    return {
        test: [{"name": "Service #1"}, {"name": "Service #2"}],
        changeService: function(service) {
            stats.menuStats['service']['change'] = service.service
            envExist = false
            service.value.envs.forEach(function(element, key) {
                if (element.env == stats.menuStats['env']['current']) {
                    envExist = true
                }
            })
            if (envExist == false) {
                stats.menuStats['env']['change'] = service.value.envs[0].env
            }
            stats.refreshData()
        },
        changeEnv: function(service, env) {
            stats.menuStats['env']['change'] = env
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
            var current_year = self.menuStats['year']['current']
            Object.keys(self.components['dates'][current_year]).forEach(function (month) {
                months.push(month)
            })
            return months
        },
        getDays: function() {
            days = []
            var current_year = self.menuStats['year']['current']
            var current_month = self.menuStats['month']['current']
            self.components['dates'][current_year][current_month].forEach(function (day) {
                days.push(day)
            })
            return days
        },
        changeYear: function(year) {
            stats.menuStats['year']['change'] = year
            stats.refreshData()
        },
        changeDay: function(day) {
            stats.menuStats['day']['change'] = day
            stats.refreshData()
        },
        changeMonth: function(month) {
            stats.menuStats['month']['change'] = month
            var current_year = stats.menuStats['year']['current']
            var current_day = stats.menuStats['day']['current']
            if (stats.inArray(current_day, self.components['dates'][current_year][month]) == false) {
                days = self.components['dates'][current_year][month]
                stats.menuStats['day']['change'] = days[days.length-1]
            }
            stats.refreshData()
        },
    }
}]);
