var ang_directives = angular.module('ang_directives', []);

ang_directives.directive('menuservicedirective', function() {
    return {
        restrict: 'EACM',
        templateUrl: '/static/scrooge/partials/leftmenu.html',
        replace: true,
        link: function (scope, element, attrs) {
        }
    }
});
ang_directives.directive('menucalendardirective', function() {
    return {
        restrict: 'EACM',
        templateUrl: '/static/scrooge/partials/calendarmenu.html',
        replace: true,
        link: function (scope, element, attrs) {
        }
    }
});
