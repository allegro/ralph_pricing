'use strict';

var scrooge = angular.module('scrooge.service', ['ngResource']);

var allocationHelper = {
    'baseUrl': '/scrooge/rest/allocationclient',
    /**
     * Return url for collect team data.
     * @param {object} menuStats - menuStats from stats.menuStats.
     */
    'getTeamsUrlChunks': function (menuStats) {
        var urlChunks = [
            this.baseUrl,
            menuStats.team.current,
            menuStats.year.current,
            menuStats.month.current
        ];
        return urlChunks;
    },
    /**
     * Return url for collect service data.
     * @param {object} menuStats - menuStats from stats.menuStats.
     */
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
    /**
     * Return url.
     * @param {string} leftMenu - name of left menu.
     * @param {object} menuStats - menuStats from stats.menuStats.
     */
    'getUrl': function (leftMenu, menuStats) {
        var urlChunks;
        switch(leftMenu) {
            case 'services':
                urlChunks = this.getServicesUrlChunks(menuStats);
                break;
            case 'teams':
                urlChunks = this.getTeamsUrlChunks(menuStats);
                break;
            default:
                throw 'Unknown leftMenu passed to fn getUrl';
        }
        return urlChunks.join('/');
    }
};

scrooge.factory('stats', ['$http', '$q', 'STATIC_URL', function ($http, $q, STATIC_URL) {
    return {
        staticUri: STATIC_URL + 'scrooge/partials/',
        cancelerDeferers: [],
        currentSubMenu: false,
        currentTab: false,
        currentTabs: {},
        menuReady: false,
        leftMenus: {},
        subMenus: {},
        menuStats: {
            'subpage': {'current': null, 'change': null},
            'team': {'current': null, 'change': null},
            'service': {'current': null, 'change': null},
            'env': {'current': null, 'change': null},
            'year': {'current': null, 'change': null},
            'month': {'current': null, 'change': null},
            'leftMenu': {'current': null, 'change': null},
            'day': {'current': null, 'change': null},
        },
        components: {
            'contentStats': {
                'table': false,
            },
        },
        cost: {
            'content': []
        },
        allocationadmin: {},
        allocationclient: {
            serviceExtraCostTypes: false,
            serviceDivision: {
                rows: [{'id': false, 'service': false, 'env': false, 'value': 0}]
            },
            serviceExtraCost: {
                rows: [{'id': false, 'value': 0, 'remarks': false}]
            },
            teamDivision: {
                rows: [{'id': false, 'service': false, 'env': false, 'value': 0}]
            }
        },
        costcard: {
            content: false,
        },
        /**
         * Called at the begin. Collect left menus and set default status for them.
         * The next step (collect data for current subpage) will base on result of this step.
         */
        init: function() {
            var self = this;
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
        /**
         * Check if something is change in menuStats and if there is a need then run refreshCurrentSubpage method
         * which is defined for each subpage in the controller.
         */
        refreshData: function() {
            var self = this;
            var force = false;
            var refresh = false;
            Object.keys(self.menuStats).forEach(function (menu) {
                if (self.menuStats[menu]['current'] != self.menuStats[menu]['change']) {
                    refresh = true;
                    self.menuStats[menu]['current'] = self.menuStats[menu]['change'];
                }
                if (menu != 'service' && menu != 'env' && menu != 'team') {
                    if (self.menuStats[menu]['change'] === null) {
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
        /**
         * Some kind of abstract function. Is defined for each subpage in top of controller body.
         */
        refreshCurrentSubpage: function () {},
        /**
         * Helper. Method check if given value is in given array.
         * It should be rewrite to indexOf().
         * @param {object} value - Checking element.
         * @param {list} array - List for check.
         */
        inArray: function(value, array) {
            for (var i in array) {
                if (array[i] == value) {
                    return true;
                }
            }
            return false;
        },
        /**
         * Collect data for components subpage.
         */
        getComponentsData: function () {
            var self = this;
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
        /**
         * Collect data for allocation client subpage.
         */
        getAllocationClientData: function () {
            var self = this;
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
        /**
         * Collect data for allocation admin subpage.
         */
        getAllocationAdminData: function () {
            var self = this;
            var url_chunks = [
                '/scrooge/rest/allocationadmin',
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
        /**
         * Collect data for cost card subpage.
         */
         getCostData: function () {
            var url_chunks = [
                '/scrooge/rest/cost',
                self.menuStats['service']['current'],
                self.menuStats['env']['current'],
                '01-01-0001',
                '02-02-0002',
            ];
            $http({
                method: 'GET',
                url: url_chunks.join('/'),
            })
            .success(function(data) {
                self.cost.content = data;
            });
        },
        getCostCardData: function () {
            var self = this;
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
                params: {forecast: true} // TEMPORARY!
            })
            .success(function(data) {
                self.costcard.content = data;
            });
        },

        /**
         * This is used for smart change subpage. When user change different subpage
         * then old data are still visible by 1 second befor everything is change.
         * This method just clean old data and make changing subpage more smart and smooth.
         */
        clearPreviousContent: function () {
            var self = this;
            self.components = {
                contentStats: {}
            };
            self.allocationclient = {};
            self.allocationadmin = {};
            self.costcard = {};
        },

        /**
         * Validating data for given tab name and when there is everything cool then
         * send POST (save) request with data.
         */
        saveAllocation: function (tab) {
            var self = this;
            var urlChunks = ['/scrooge/rest/allocationclient'], data = {}, error = false;

            // Validators with valid method. Should be move to separated service?
            var valid_service = function (row) {
                if (typeof(row.env) === 'undefined') {
                    error = true;
                    row.errors['env'] = 'Please choose environment.';
                }
            };
            var valid_env = function (row) {
                if (row.service === false) {
                    error = true;
                    row.errors['service'] = 'Please choose service.';
                }
            };
            var valid_value = function (row) {
                if (row.value === 0) {
                    error = true;
                    row.errors['value'] = 'Type value.';
                }
            };
            var valid = function (obj, validators) {
                obj.forEach(function (row) {
                    row.errors = {};
                    validators.forEach(function (validator) {
                        validator(row);
                    });
                });
            };
            switch(tab) {
                case 'serviceDivision':
                    urlChunks.push(self.menuStats['service']['current']);
                    urlChunks.push(self.menuStats['env']['current']);
                    urlChunks.push(self.menuStats['year']['current']);
                    urlChunks.push(self.menuStats['month']['current']);
                    urlChunks.push('servicedivision/save/');
                    data = {'rows': self.currentTabs.serviceDivision.rows};
                    valid(data.rows, [valid_service, valid_env]);
                    break;
                case 'serviceExtraCost':
                    urlChunks.push(self.menuStats['service']['current']);
                    urlChunks.push(self.menuStats['env']['current']);
                    urlChunks.push(self.menuStats['year']['current']);
                    urlChunks.push(self.menuStats['month']['current']);
                    urlChunks.push('serviceextracost/save/');
                    data = {'rows': self.currentTabs.serviceExtraCost.rows};
                    valid(data.rows, [valid_value]);
                    break;
                case 'teamDivision':
                    urlChunks.push(self.menuStats['team']['current']);
                    urlChunks.push(self.menuStats['year']['current']);
                    urlChunks.push(self.menuStats['month']['current']);
                    urlChunks.push('teamdivision/save/');
                    data = {'rows': self.currentTabs.teamDivision.rows};
                    valid(data.rows, [valid_service, valid_env]);
                    break;
            }
            if (error === false) {
                $http({
                    url: urlChunks.join('/'),
                    method: 'POST',
                    data: data,
                });
            }
        },
        getEnvs: function (service_id) {
            var self = this;
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
            var self = this;
            self.currentTab = tab;
        },
        getFirstExistMenu: function () {
            var self = this;

            for (var i in self.leftMenus) {
                if (self.inArray(i, self.currentSubMenu.leftMenu) === true) {
                    return i;
                }
            }
            return false;
        },
        /**
         * Return url for html template for current tab.
         */
        getCurrentTab: function() {
            var self = this;

            if (Object.keys(self.currentTabs).length > 0) {
                return self.staticUri + self.currentTabs[self.currentTab].template;
            }
        }
    };
}]);
