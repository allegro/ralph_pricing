var ang_directives = angular.module('ang_directives', []);

ang_directives.directive('chart', ['_', function (_) {
    return {
        restrict: 'EACM',
        template: '<div></div>',
        replace: true,
        link: function (scope, element, attrs) {
            var createChart = function () {
                var data = [[[1, 2],[3,5.12],[5,13.1],[7,33.6],[9,85.9],[11,219.9]]]
                var opts = {};
                element.html('');
                if (!angular.isArray(data) || _.isEmpty(_.flatten(data))) {
                    element.html('Please provide some data for this question domain first.');
                    return;
                }
                if (!angular.isUndefined(attrs.chartOptions)) {
                    opts = scope.$eval(attrs.chartOptions);
                    if (!angular.isObject(opts)) {
                        throw 'Invalid myChart options attribute';
                    }
                }
                // that gives 'Object has no method jqplot' in modal - which is
                // kind of strange, because w/o modal it works - there must be
                // some mess in my controller (or modal directive), I guess...
                //element.jqplot(data, opts);
                $(element).jqplot(data, opts);
            };  // createChart

            scope.$watch(attrs.chartData, function () {
                createChart();
            }, true);

            scope.$watch(attrs.chartOptions, function () {
                createChart();
            });

            element.bind('jqplotDataClick', function (ev, seriesIndex, pointIndex, data) {
                scope.$broadcast('event:jqplotDataClick', data[4]);  // data[4] === audit_id
            });
        }  // link
    };
}]);
