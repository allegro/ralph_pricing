var ang_services = angular.module('ang_services', ['ngResource']);

ang_services.factory('stats', ['$http', function ($http) {
    return {
        contentReady: 0,
        currentMenu: false,
        currentTab: false,
        menuReady: false,
        menus: false,
        menuStats: {
            "subpage": {"current": false, "change": false},
            "team": {"current": false, "change": false},
            "service": {"current": false, "change": false},
            "env": {"current": false, "change": false},
            "year": {"current": false, "change": false},
            "month": {"current": false, "change": false},
            "day": {"current": false, "change": false},
        },
        components: {
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
            serviceExtraCostTypes: false,
            serviceDivision: {
                total: 0,
                rows: [{"service": false, "env": false, "value": 0}]
            },
            serviceExtraCost: {
                rows: [{"id": false, "type": false, "value": 0, "remarks": false}]
            },
            teamDivision: {
                total: 0,
                rows: [{"id": false, "service": false, "env": false, "value": 0}]
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
                    self.dates = data["dates"]
                    self.currentMenu = Object.keys(self.menus)[0]
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
        refreshData: function() {
            self = this
            force = false
            refresh = false
            Object.keys(self.menuStats).forEach(function (menu) {
                if (self.menuStats[menu]['current'] != self.menuStats[menu]['change']) {
                    refresh = true
                    self.menuStats[menu]['current'] = self.menuStats[menu]['change']
                }
                if (menu != 'service' && menu != 'env' && menu != 'team') {
                    if (self.menuStats[menu]['change'] == false) {
                        force = true
                    }
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
            self.contentReady += 1
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
                self.contentReady -= 1
                self.components.contentStats.table = data[0].name
            }).
            error(function(data, status, headers, config) {
                self.contentReady -= 1
            });
        },
        getAllocationClientData: function () {
            self.contentReady += 1
            $http({
                method: 'GET',
                url: '/scrooge/allocateclient/'
                    + self.menuStats['service']['current'] + '/'
                    + self.menuStats['env']['current'] + '/'
                    + self.menuStats['team']['current'] + '/'
                    + self.menuStats['year']['current'] + '/'
                    + self.menuStats['month']['current'] + '/'
            }).
            success(function(data, status, headers, config) {
                if (data) {
                    data.forEach(function (element) {
                        self.allocationclient[element.key] = element.value
                        if (element.value.rows.length <= 1 || element.value.disabled == true) {
                            element.value.rows = [{}]
                        }
                        if (element.key == 'serviceExtraCost') {
                            self.allocationclient.serviceExtraCostTypes = element.extra_cost_types
                        }
                    })
                }
                self.contentReady -= 1
            }).
            error(function(data, status, headers, config) {
                self.contentReady -= 1
            });
        },
        saveAllocation: function (tab) {
            switch(tab) {
                case 'serviceDivision':
                    url = '/scrooge/allocateclient/servicedivision/save/'
                    data = {
                        "service": self.menuStats['service']['current'],
                        "rows": self.allocationclient.serviceDivision.rows,
                    }
                    break;
                case 'serviceExtraCost':
                    url = '/scrooge/allocateclient/serviceextracost/save/'
                    data = {
                        'service': self.menuStats['service']['current'],
                        "env": self.menuStats['env']['current'],
                        'rows': self.allocationclient.serviceExtraCost.rows,
                    }
                    break;
                case 'teamDivision':
                    url = '/scrooge/allocateclient/teamdivision/save/'
                    data = {
                        'team': self.menuStats['team']['current'],
                        'rows': self.allocationclient.teamDivision.rows,
                    }
                    break;
                default:
                    url = ''
                    data = {}
            }
            data['month'] = self.menuStats['month']['current']
            data['year'] = self.menuStats['year']['current']
            $http({
                url: url,
                method: 'POST',
                data: data,
            }).
            success(function(data, status, headers, config) {

            }).
            error(function(data, status, headers, config) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
            });
        },
        getEnvs: function (service) {
            var envs = []
            if (self.menus) {
                self.menus['service'].forEach(function (element) {
                    if (element.service == service) {
                        envs = element.value.envs
                    }
                })
            }
            return envs
        },
        changeTab: function (tab) {
            self.currentTab = tab
        }
    }
}]);

ang_services.factory('menuService', ['stats', '$http', function (stats, $http) {
    return {
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
            if (typeof(self.dates) != 'undefined') {
                Object.keys(self.dates).forEach(function (year) {
                    years.push(year)
                })
            }
            return years
        },
        getMonths: function() {
            months = []
            if (typeof(self.dates) != 'undefined') {
                var current_year = self.menuStats['year']['current']
                Object.keys(self.dates[current_year]).forEach(function (month) {
                    months.push(month)
                })
            }
            return months
        },
        getDays: function() {
            days = []
            if (typeof(self.dates) != 'undefined') {
                var current_year = self.menuStats['year']['current']
                var current_month = self.menuStats['month']['current']
                self.dates[current_year][current_month].forEach(function (day) {
                    days.push(day)
                })
            }
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
            if (stats.inArray(current_day, self.dates[current_year][month]) == false) {
                days = self.dates[current_year][month]
                stats.menuStats['day']['change'] = days[days.length-1]
            }
            stats.refreshData()
        },
    }
}]);
