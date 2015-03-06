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
                urlChunks = [];
        }
        return urlChunks.join('/');
    }
};

scrooge.factory('stats', ['$http', '$q', '$routeParams', '$location', 'STATIC_URL', 'REST_URLS', function ($http, $q, $routeParams, $location, STATIC_URL, REST_URLS) {
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
            'day': {'current': null, 'change': null},
            'startDate': {'current': null, 'change': null},
            'endDate': {'current': null, 'change': null},
            'leftMenu': {'current': null, 'change': null},
        },
        components: {
            'contentStats': {
                'table': false,
            },
        },
        cost: {
            'content': [],
            'contentStats': {
                'table': false,
            }
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
            var refresh = false;
            Object.keys(self.menuStats).forEach(function (menu) {
                if (self.menuStats[menu]['current'] != self.menuStats[menu]['change']) {
                    refresh = true;
                    self.menuStats[menu]['current'] = self.menuStats[menu]['change'];
                }
            });
            if (refresh === true) {
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
            if (self.menuStats['service']['current'] &&
                self.menuStats['year']['current'] &&
                self.menuStats['month']['current'] &&
                self.menuStats['day']['current']) {
                var url_chunks = [
                    '/scrooge/rest/components',
                    self.menuStats['service']['current'],
                ];
                if (self.menuStats['env']['current']) {
                    url_chunks.push(self.menuStats['env']['current']);
                }
                url_chunks = url_chunks.concat([
                    self.menuStats['year']['current'],
                    self.menuStats['month']['current'],
                    self.menuStats['day']['current'],
                ]);
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
            }
        },
        /**
         * Collect data for allocation client subpage.
         */
        getAllocationClientData: function () {
            var self = this;
            if (self.menuStats['service']['current'] &&
                self.menuStats['year']['current'] &&
                self.menuStats['month']['current'] &&
                self.menuStats['day']['current']) {
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
            }
        },
        /**
         * Collect data for allocation admin subpage.
         */
        getAllocationAdminData: function () {
            var self = this;
            if (self.menuStats['year']['current'] &&
                self.menuStats['month']['current']) {
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
                        self.currentTabs = self.allocationadmin;
                        if (!self.currentTab || !(self.currentTab in self.currentTabs)) {
                            self.changeTab(Object.keys(self.allocationadmin)[0]);
                        }
                    }
                });
            }
        },
        /**
         * Collect data for cost card subpage.
         */
         getCostData: function () {
            var self = this;
            if (self.menuStats['service']['current'] &&
                self.menuStats['startDate']['current'] &&
                self.menuStats['endDate']['current'] &&
                self.menuStats['env']['current']) {
                if(self.menuStats['startDate']['current'] && self.menuStats['endDate']['current']) {
                    var start = self.menuStats['startDate']['current'];
                    var end = self.menuStats['endDate']['current'];
                    var url_chunks = [
                        '/scrooge/rest/pricing_object_costs',
                        self.menuStats['service']['current'],
                        self.menuStats['env']['current'],
                        start.getFullYear() + '-' + (start.getMonth() + 1) + '-' + start.getDate(),
                        end.getFullYear() + '-' + (end.getMonth() + 1) + '-' + end.getDate(),
                    ];
                    $http({
                        method: 'GET',
                        url: url_chunks.join('/'),
                    })
                    .success(function(data) {
                        self.cost.content = data;
                        self.cost.contentStats.table = data[0].name;
                    });
                }
            }
        },
        getCostCardData: function () {
            var self = this;
            if (self.menuStats['service']['current'] &&
                self.menuStats['year']['current'] &&
                self.menuStats['month']['current'] &&
                self.menuStats['env']['current']) {
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
                    if (data && data.status) {
                        self.costcard.content = data.results;
                    } else {
                        self.costcard.error_message = data.message;
                    }
                });
            }
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
            var urlClientChunks = [REST_URLS.ALLOCATION_CLIENT],
                urlAdminChunks = [REST_URLS.ALLOCATION_ADMIN],
                data = {},
                error = false,
                urlChunks = false;
            // Validators with valid method. Should be move to separated service?
            var valid_env = function (row) {
                var badEnv = false;
                if (row.env === false || typeof(row.env) === 'undefined') {
                    badEnv = true;
                }
                var exist = false;
                self.getEnvs(row.service).forEach(function (env) {
                    if (env.id === row.env) {
                        exist = true;
                    }
                });
                if (badEnv || !exist) {
                    error = true;
                    row.errors['env'] = 'Please choose environment.';
                }
            };
            var valid_service = function (row) {
                if (row.service === false || typeof(row.service) === 'undefined') {
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
                    urlClientChunks.push(self.menuStats['service']['current']);
                    urlClientChunks.push(self.menuStats['env']['current']);
                    urlClientChunks.push(self.menuStats['year']['current']);
                    urlClientChunks.push(self.menuStats['month']['current']);
                    urlClientChunks.push('servicedivision/save/');
                    urlChunks = urlClientChunks;
                    data = {'rows': self.currentTabs.serviceDivision.rows};
                    valid(data.rows, [valid_service, valid_env]);
                    break;
                case 'serviceExtraCost':
                    urlClientChunks.push(self.menuStats['service']['current']);
                    urlClientChunks.push(self.menuStats['env']['current']);
                    urlClientChunks.push(self.menuStats['year']['current']);
                    urlClientChunks.push(self.menuStats['month']['current']);
                    urlClientChunks.push('serviceextracost/save/');
                    urlChunks = urlClientChunks;
                    data = {'rows': self.currentTabs.serviceExtraCost.rows};
                    valid(data.rows, [valid_value]);
                    break;
                case 'teamDivision':
                    urlClientChunks.push(self.menuStats['team']['current']);
                    urlClientChunks.push(self.menuStats['year']['current']);
                    urlClientChunks.push(self.menuStats['month']['current']);
                    urlClientChunks.push('teamdivision/save/');
                    urlChunks = urlClientChunks;
                    data = {'rows': self.currentTabs.teamDivision.rows};
                    valid(data.rows, [valid_service, valid_env]);
                    break;
                case 'baseusages':
                    urlAdminChunks.push(self.menuStats['year']['current']);
                    urlAdminChunks.push(self.menuStats['month']['current']);
                    urlAdminChunks.push('baseusages/save/');
                    urlChunks = urlAdminChunks;
                    data = {'rows': self.currentTabs.baseusages.rows};
                    break;
                case 'dynamicextracosts':
                    urlAdminChunks.push(self.menuStats['year']['current']);
                    urlAdminChunks.push(self.menuStats['month']['current']);
                    urlAdminChunks.push('dynamicextracosts/save/');
                    urlChunks = urlAdminChunks;
                    data = {'rows': self.currentTabs.dynamicextracosts.rows};
                    break;
                case 'extracostsadmin':
                    urlAdminChunks.push(self.menuStats['year']['current']);
                    urlAdminChunks.push(self.menuStats['month']['current']);
                    urlAdminChunks.push('extracosts/save/');
                    urlChunks = urlAdminChunks;
                    data = {'rows': self.currentTabs.extracosts.rows};
                    data.rows.forEach(function (row) {
                        if (Object.keys(row.extra_costs[0]).length > 1) {
                            valid(row.extra_costs, [valid_service, valid_env]);
                        }
                    });
                    break;
                case 'teamcosts':
                    urlAdminChunks.push(self.menuStats['year']['current']);
                    urlAdminChunks.push(self.menuStats['month']['current']);
                    urlAdminChunks.push('teamcosts/save/');
                    urlChunks = urlAdminChunks;
                    data = {'rows': self.currentTabs.teamcosts.rows};
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
            $routeParams.tab = tab;
            var newPath = $location.path().split('/');
            newPath[3] = tab;
            $location.path(newPath.join('/'));
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

            if (Object.keys(self.currentTabs).length > 0 &&
                self.currentTab in self.currentTabs) {
                return self.staticUri + self.currentTabs[self.currentTab].template;
            }
        }
    };
}]);
