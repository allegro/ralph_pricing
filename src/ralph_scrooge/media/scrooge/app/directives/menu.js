var scrooge = angular.module('scrooge.directives', []);

scrooge.directive('subMenu', function() {
    return {
        restrict: 'EA',
        templateUrl: '/static/scrooge/partials/sub_menu.html',
        controller: 'SubMenuCtrl',
    };
});
