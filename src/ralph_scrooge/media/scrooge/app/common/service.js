'use strict';

var scrooge = angular.module('scrooge.service', ['ngResource']);

var allocationHelper = {
    'baseUrl': '/scrooge/rest/allocateclient',

    'getTeamsUrlChunks': function (menuStats) {
        var urlChunks = [
            this.baseUrl,
            menuStats.team.current,
            menuStats.year.current,
            menuStats.month.current
        ];
        return urlChunks;
    },
    'getServicesUrlChunks': function (menuStats) {
        var urlChunks = [
            this.baseUrl,
            menuStats.service.current,
            menuStats.env.current,
            menuStats.year.current,
            menuStats.month.current
        ];
        return urlChunks;
    },
    'getUrl': function (leftMenu, menuStats) {
        var urlChunks;
        if (leftMenu === 'services') {
            urlChunks = this.getServicesUrlChunks(menuStats);
        } else if (leftMenu === 'teams') {
            urlChunks = this.getTeamsUrlChunks(menuStats);
        } else {
            throw "Unknown leftMenu passed to fn getUrl";
        }
        return urlChunks.join('/');
    }
};


scrooge.factory('stats', ['$http', '$q', function ($http, $q) {
    return {
        staticUri: '/static/scrooge/partials/',
        cancelerDeferers: [],
        currentSubMenu: false,
        //currentLeftMenu: false,
        currentTab: false,
        currentTabs: {},
        menuReady: false,
        leftMenus: {},
        subMenus: {},
        menuStats: {
            'subpage': {'current': false, 'change': false},
            'team': {'current': false, 'change': false},
            'service': {'current': false, 'change': false},
            'env': {'current': false, 'change': false},
            'year': {'current': false, 'change': false},
            'month': {'current': false, 'change': false},
            'leftMenu': {'current': false, 'change': false},
            'day': {'current': false, 'change': false},
        },
        components: {
            'contentStats': {
                'table': false,
            },
        },
        allocationadmin: {},
        allocationclient: {
            serviceExtraCostTypes: false,
            serviceDivision: {
                total: 0,
                rows: [{'service': false, 'env': false, 'value': 0}]
            },
            serviceExtraCost: {
                rows: [{'id': false, 'name': false, 'value': 0, 'remarks': false}]
            },
            teamDivision: {
                total: 0,
                //rows: [{'id': false, 'name': false}]
                rows: [{'service': false, 'env': false, 'value': 0}]
            }
        },
        costcard: {
            content: false,
        },
        init: function() {
            self = this;
            $http({method: 'GET', url: '/scrooge/leftmenu/components/'}).
                success(function(data) {
                    Object.keys(data['menuStats']).forEach(function (key){
                        self.menuStats[key] = data['menuStats'][key];
                    });
                    self.leftMenus = data['menus'];
                    self.dates = data['dates'];
                    self.menuStats.leftMenu['change'] = Object.keys(self.leftMenus)[0];
                    self.refreshData();
                });
        },
        isLeapYear: function (year) {
            return ((year % 4 === 0) && (year % 100 !== 0)) || (year % 400 === 0);
        },
        daysInMonth: function (date) {
            return [31, (this.isLeapYear(date.getYear()) ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        },
        refreshData: function() {
            self = this;
            var force = false;
            var refresh = false;
            Object.keys(self.menuStats).forEach(function (menu) {
                if (self.menuStats[menu]['current'] != self.menuStats[menu]['change']) {
                    refresh = true;
                    self.menuStats[menu]['current'] = self.menuStats[menu]['change'];
                }
                if (menu != 'service' && menu != 'env' && menu != 'team') {
                    if (self.menuStats[menu]['change'] === false) {
                        force = true;
                    }
                }
            });
            if (force === false && refresh === true) {
                self.clearPreviousContent();
                self.refreshCurrentSubpage();
            }
            if (self.menuReady === false) {
                self.menuReady = true;
            }
        },
        refreshCurrentSubpage: function () {},
        inArray: function(value, array) {
            for (var i in array) {
                if (array[i] == value) {
                    return true;
                }
            }
            return false;
        },
        getComponentsData: function () {
            var url_chunks = [
                '/scrooge/components',
                self.menuStats['service']['current'],
                self.menuStats['env']['current'],
                self.menuStats['year']['current'],
                self.menuStats['month']['current'],
                self.menuStats['day']['current'],
            ];
            if (typeof(self.canceler) !== 'undefined') {
                self.canceler.resolve();
            }
            self.canceler = $q.defer();
            $http({
                method: 'GET',
                url: url_chunks.join('/'),
                timeout: self.canceler.promise,
            }).
            success(function(data) {
                self.components.content = data;
                self.components.contentStats.table = data[0].name;
            });
        },
        getAllocationClientData: function () {
            /*
             * Load allocation data
             */
            $http({
                method: 'GET',
                url: allocationHelper.getUrl(
                    self.menuStats.leftMenu.current, self.menuStats
                )
            })
            .success(function(data) {
                if (data) {
                    Object.keys(data).forEach(function (key) {
                        self.allocationclient.data = data;
                        if (data[key].rows.length === 0 || data[key].disabled === true) {
                            data[key].rows = [{}];
                        }
                    });
                    self.currentTabs = self.allocationclient.data;
                    var tabs = Object.keys(self.allocationclient.data);
                    self.currentTab = tabs[tabs.length - 1];
                }
            });
        },
        getAllocationAdminData: function () {
            /**
             * Load admin allocation data
             */
            var url_chunks = [
                '/scrooge/rest/allocateadmin',
                self.menuStats['year']['current'],
                self.menuStats['month']['current'],
            ];
            $http({
                method: 'GET',
                url: url_chunks.join('/'),
            })
            .success(function(data) {
                if (data) {
                    Object.keys(data).forEach(function (element) {
                        self.allocationadmin[element] = data[element];
                        if (data[element].rows.length === 0 || data[element].disabled === true) {
                            self.allocationadmin[element].rows = [{}];
                        }
                    });
                    self.currentTabs = self.allocationclient;
                    self.currentTab = Object.keys(self.allocationadmin)[0];
                }
            });
        },
        getCostCardData: function () {
            /**
             * Load cost card data
             */
            var url_chunks = [
                '/scrooge/rest/costcard',
                self.menuStats['service']['current'],
                self.menuStats['env']['current'],
                self.menuStats['year']['current'],
                self.menuStats['month']['current'],
            ];
            $http({
                method: 'GET',
                url: url_chunks.join('/'),
            })
            .success(function(data) {
                self.costcard.content = data;
            });
        },
        clearPreviousContent: function () {
            self.components = {
                contentStats: {}
            };
            self.allocationclient = {};
            self.allocationadmin = {};
            self.costcard = {};
        },
        saveAllocation: function (tab) {
            var url = '';
            var data = {};
            switch(tab) {
                case 'serviceDivision':
                    url = '/scrooge/allocateclient/servicedivision/save/';
                    data = {
                        'service': self.menuStats['service']['current'],
                        'rows': self.currentTabs.serviceDivision.rows,
                    };
                    break;
                case 'serviceExtraCost':
                    url = '/scrooge/allocateclient/serviceextracost/save/';
                    data = {
                        'service': self.menuStats['service']['current'],
                        'env': self.menuStats['env']['current'],
                        'rows': self.currentTabs.serviceExtraCost.rows,
                    };
                    break;
                case 'teamDivision':
                    url = '/scrooge/allocateclient/teamdivision/save/';
                    data = {
                        'team': self.menuStats['team']['current'],
                        'rows': self.currentTabs.teamDivision.rows,
                    };
                    break;
            }
            data['month'] = self.menuStats['month']['current'];
            data['year'] = self.menuStats['year']['current'];
            $http({
                url: url,
                method: 'POST',
                data: data,
            });
        },
        getEnvs: function (service_id) {
            var envs = [];
            if (Object.keys(self.leftMenus).length > 0) {
                self.leftMenus['services'].forEach(function (element) {
                    if (element.id == service_id) {
                        envs = element.value.envs;
                    }
                });
            }
            return envs;
        },
        changeTab: function (tab) {
            self.currentTab = tab;
        },
        getFirstExistMenu: function () {
            for (var i in self.leftMenus) {
                if (self.inArray(i, self.currentSubMenu.leftMenu) === true) {
                    return i;
                }
            }
            return false;
        },
        getCurrentTab: function() {
            if (Object.keys(self.currentTabs).length > 0) {
                return self.staticUri + self.currentTabs[self.currentTab].template;
            }
        }
    };
}]);
