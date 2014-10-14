var app = angular.module('app', [
    'ngRoute',
    'ngCookies',

    'ang_controllers',
    'ang_directives',
    'ang_services',
]);

app.config(['$routeProvider', '$httpProvider', '$provide',
    function($routeProvider, $httpProvider, $provide) {

        // we want Sentry to log our exceptions...
        //$provide.decorator("$exceptionHandler", function($delegate) {
        //    Raven.config('', {}).install();
        //    return function(exception, cause) {
        //        $delegate(exception, cause);
        //        Raven.captureException(exception);
        //    };
        //});
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $httpProvider.interceptors.push(function ($q) {
            return {
                responseError: function (rejection) {
                    // if the backend returns 401/403 it means that we should log in first
                    if (rejection.status === 401 || rejection.status === 403) {
                        window.location.replace('/login/');
                    } else {
                        // we want to catch XHR errors as well (XXX doesn't work by now)
                        // Raven.config('', {}).install();
                        // Raven.captureException(new Error('HTTP response error'), {
                        //     extra: {
                        //         config: rejection.config,
                        //         status: rejection.status,
                        //     }
                        // });
                    };
                    return $q.reject(rejection);
                }
            }
        });
        $routeProvider.
            when('/components/', {
                templateUrl: '/static/scrooge/partials/components.html',
                controller: 'componentsCtrl',
            }).
            when('/allocation/client/', {
                templateUrl: '/static/scrooge/partials/allocationclient.html',
                controller: 'allocationClientCtrl',
            }).
            otherwise({redirectTo: '/components/'});
    }
]);

app.run(function($http, $cookies, $rootScope) {
    $http.defaults.headers.common['x-csrftoken'] = $cookies.csrftoken;

    $http.get('/api/current_user/').success(function (data) {
        $rootScope.$broadcast('event:user-loggedin', data);
    });
});
