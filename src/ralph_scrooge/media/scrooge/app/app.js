angular.module('underscore', []).factory('_', ['$window', function ($window) {
    return $window._;
}]);

var app = angular.module('app', [
    'ngRoute',
    'ngCookies',

    'ui.bootstrap', // Alternatywa
    'underscore',
    'flash',

    'ang_controllers',
]);

app.config(['$routeProvider', '$httpProvider', '$provide',
    function($routeProvider, $httpProvider, $provide) {

        // we want Sentry to log our exceptions...
        $provide.decorator("$exceptionHandler", function($delegate) {
            Raven.config('http://b4a72068092b475dba6917630417336f@ralph-sentry.office/21', {}).install();
            return function(exception, cause) {
                $delegate(exception, cause);
                Raven.captureException(exception);
            };
        });

        $httpProvider.interceptors.push(function ($q) {
            return {
                responseError: function (rejection) {
                    // if the backend returns 401/403 it means that we should log in first
                    if (rejection.status === 401 || rejection.status === 403) {
                        window.location.replace('/login/');
                    } else {
                        // we want to catch XHR errors as well (XXX doesn't work by now)
                        // Raven.config('http://d9fa5c1a334f4b02822ae7a18bad04ae@ralph-sentry.office/10', {}).install();
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
            when('/scrooge/components/', {
                templateUrl: '/static/scrooge/partials/components2.html',
                controller: 'components',
            }).
            otherwise({redirectto: '/scrooge'});
    }
]);

app.run(function($http, $cookies, $rootScope) {
    $http.defaults.headers.common['x-csrftoken'] = $cookies.csrftoken;

    $http.get('/api/current_user/').success(function (data) {
        $rootScope.$broadcast('event:user-loggedin', data);
    });
});
