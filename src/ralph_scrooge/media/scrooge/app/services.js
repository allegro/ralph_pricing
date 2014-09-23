var ang_services = angular.module('ang_services', ['ngResource']);

ang_services.factory('menuService', ['$http', function ($http) {
    return {
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
    	init: function() {
    		//Getting and prepare data
    	},
        getLeftMenu: function(params) {
        	return this.menu
        },
        changeService: function(service) {
        	var self = this
            Object.keys(self.menu).forEach(function (scopeService) {
        		self.menu[scopeService]['show'] = false
            })
    		self.menu[service]['show'] = true
    		this.menuStats['service']['change'] = service
        	this.refreshData()
        },
        changeEnv: function(service, env) {
        	var self = this
            Object.keys(self.menu).forEach(function (scopeService) {
        		self.menu[scopeService]['envs'].forEach(function (envScope) {
	        		if (env.env == envScope.env && scopeService == service) {
	        			envScope.show = true;
	        		} else {
	        			envScope.show = false;
	        		}
           		});
        	});
        	this.menuStats['env']['change'] = env.env
        	this.refreshData()
        },
        checkActiveService: function(service) {
        	return this.menu[service]['show']
        },
        checkActiveEnv: function(service, env) {
        	return_value = false
        	test = this.menu[service]['envs'].forEach(function (envScope) {
        		if (env.env == envScope.env) {
        			if (envScope.show == true) {
        				return_value = true
        			}
        		}
        	})
        	return return_value
        },
        refreshData: function() {
            self = this
            force = false
            refresh = false
            Object.keys(self.menuStats).forEach(function (menu) {
                if (self.menuStats[menu]['change'] == false) {
                    force = true
                }
                if (self.menuStats[menu]['current'] != self.menuStats[menu]['change']) {
                    refresh = true
                }
            })
            console.log(force, refresh, self.menuStats)
        }
    }
}]);
