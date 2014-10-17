var scrooge = angular.module('scrooge.directives', []);

scrooge.directive('mainMenu', function() {
	return {
		restrict: 'EA',
		templateUrl: '/static/scrooge/partials/main_menu.html',
		controller: 'MainMenuCtrl',
	};
});
