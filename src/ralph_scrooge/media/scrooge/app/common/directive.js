'use strict';

var scrooge = angular.module('scrooge.directive', []);

scrooge.directive('tabsdirective', function() {
    return {
        restrict: 'EACM',
        templateUrl: '/static/scrooge/partials/tabs.html',
        replace: true,
    };
});