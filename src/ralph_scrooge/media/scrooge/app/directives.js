google.load('visualization', '1', {'packages': ['corechart', 'controls', 'orgchart']});

var ang_directives = angular.module('ang_directives', ['googlechart']);

ang_directives.directive('costchart', ['_', function (_) {
    return {
        restrict: 'EACM',
        template: '<div></div>',
        scope: {
            data: '=',
            seriescolors: '=',
        },
        replace: true,
        link: function (scope, element, attrs) {
            var createChart = function () {
                // that gives 'Object has no method jqplot' in modal - which is
                // kind of strange, because w/o modal it works - there must be
                // some mess in my controller (or modal directive), I guess...
                //element.jqplot(data, opts);
                //
                scope.$watch(function () {
                    var data = scope.data
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

                    opts = {
                        textColor:"#ff0000",
                        grid:{shadow:false, borderWidth:9.0},
                        seriesColors: scope.seriescolors,
                        gridPadding:{right:35},
                        axes:{
                            xaxis:{
                                label:'Months',
                                renderer:$.jqplot.DateAxisRenderer,
                                tickOptions:{formatString:'%b %#d, %y'},
                                min:'January 30, 2015',
                                tickInterval:'1 month',
                                Options:{
                                    formatString:'%b&nbsp;%#d'
                                },
                            },
                            yaxis:{
                                label:'Cost(zł)',
                                tickOptions:{
                                    formatString:'$%.2f',
                                },
                            },
                        },
                        highlighter: {
                            show: true,
                            sizeAdjust: 7.5
                        },
                        cursor: {
                            show: false
                        },
                        series:[{
                            lineWidth:4,
                            markerOptions:{style:'circle'},
                            showMarker: true
                        }],
                        pointLabels: { show:true, location: 'ne' } // do not show marker, but do show point label
                    };

                    var line1=[['2015-06-30 1:00AM',4], ['2008-10-30 8:00AM',8.2]];

                    $(element).jqplot(data, opts);
                })
            };  // createChart

            scope.$watch(attrs.currentchartData, function () {
                createChart();
            }, true);

            element.bind('jqplotDataClick', function (ev, seriesIndex, pointIndex, data) {
                scope.$broadcast('event:jqplotDataClick', data[4]);  // data[4] === audit_id
            });
        }  // link
    };
}]);

ang_directives.directive('orgchart', function() {
      return {
        restrict: 'EACM',
        link: function($scope, $elm) {
          wrapper = new google.visualization.ChartWrapper($scope.chartObject);
          wrapper.draw()
          $(wrapper.m).find('td[title="service_main"]').append($('<div class="panel-tree">test</div>'))
          google.visualization.events.addListener(wrapper, 'select', function () {
          });
        }
      }
});

ang_directives.directive('leftmenudirective', function() {
    return {
        restrict: 'EACM',
        templateUrl: 'http://127.0.0.1:8000/static/scrooge/partials/leftmenu.html',
        replace: true,
        link: function (scope, element, attrs) {
            console.log('!!!!!!')
        }
    }
});
