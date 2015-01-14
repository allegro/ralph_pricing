'use strict';

describe('Controller: mainCtrl', function () {
    beforeEach(module('app'));

    var scope;
    beforeEach(inject(function($controller, $rootScope) {
        scope = $rootScope.$new();
        $controller('mainCtrl', {
            $scope: scope
        });
    }));

    it('Method: getDictLength should return 1', function () {
        expect(scope.getDictLength({'test': 'test'})).toEqual(1);
    });
    it('Scope: stats should be exist', function () {
        expect(typeof(scope.stats)).not.toBe('undefined');
    });
    it('Scope: menuCalendar should be exist', function () {
        expect(typeof(scope.menuCalendar)).not.toBe('undefined');
    });
    it('Scope: menuService should be exist', function () {
        expect(typeof(scope.menuService)).not.toBe('undefined');
    });
});

