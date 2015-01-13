'use strict';

var scrooge = angular.module('scrooge.directive.menu', []);

scrooge.directive('subMenu', function() {
    return {
        restrict: 'EA',
        templateUrl: '/static/scrooge/partials/sub_menu.html',
        controller: 'SubMenuCtrl',
    };
});

scrooge.directive('menuservicedirective', function() {
    return {
        restrict: 'EACM',
        templateUrl: '/static/scrooge/partials/leftmenu.html',
        replace: true,
    };
});

scrooge.directive('menucalendardirective', function() {
    return {
        restrict: 'EACM',
        templateUrl: '/static/scrooge/partials/calendarmenu.html',
        replace: true,
    };
});
