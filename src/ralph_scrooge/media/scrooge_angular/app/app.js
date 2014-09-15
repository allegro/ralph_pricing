angular.module('underscore', []).factory('_', ['$window', function ($window) {
    return $window._;
}]);

var app = angular.module('app', [
    'ngRoute',
    'ngCookies',

    'ui.bootstrap',
    'underscore',
    'flash',

    'ang_controllers',
    'ang_directives',
    'ang_services',
    'ang_filters',
]);

app.config(['$routeProvider', '$httpProvider', '$provide',
    function($routeProvider, $httpProvider, $provide) {

        // we want Sentry to log our exceptions...
        $provide.decorator("$exceptionHandler", function($delegate) {
            Raven.config('http://d9fa5c1a334f4b02822ae7a18bad04ae@ralph-sentry.office/10', {}).install();
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
            when('/modules', {
                templateUrl: 'static/partials/modules.html',
            }).
            when('/:module/home', {
                templateUrl: 'static/partials/home.html',
                controller: 'homeCtrl'
            }).
            when('/:module/all_audits', {
                templateUrl: 'static/partials/all_audits.html',
                controller: 'allAuditsCtrl'
            }).
            when('/:module/audit_reviews', {
                templateUrl: 'static/partials/audit_reviews.html',
                controller: 'auditReviewsCtrl'
            }).
            when('/:module/audit_review_details/:id', {  // id of auditable, not audit
                templateUrl: 'static/partials/audit_review_details.html',
                controller: 'auditReviewDetailsCtrl',
            }).
            when('/:module/edit_audit/', {
                templateUrl: 'static/partials/edit_audit_form.html',
                controller: 'editAuditCtrl',
            }).
            otherwise({redirectTo: '/modules'});
    }
]);

app.run(function($http, $cookies, $rootScope) {
    $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;

    $http.get('/api/current_user/').success(function (data) {
        $rootScope.$broadcast('event:user-loggedIn', data);
    });
});
