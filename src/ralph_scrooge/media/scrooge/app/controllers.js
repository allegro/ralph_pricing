var ang_controllers = angular.module('ang_controllers', ['googlechart']);

ang_controllers.controller('components', ['$scope', '$routeParams', function ($scope, $routeParams) {
    $scope.models = [{
        Name: "HP ProLiant DL 360 G6",
        Selected: true,
    }, {
        Name: "HP ProLiant BL2x220c G5",
        Selected: true,
    }, {
        Name: "HP ProLiant DL 360 G6",
        Selected: true,
    }, {
        Name: "IBM BladeCenter HS21",
        Selected: true,
    }, {
        Name: "HP ProLiant BL2x220c G5",
        Selected: true,
    }, {
        Name: "HP ProLiant BL2x220c G5",
        Selected: true,
    }, {
        Name: "IBM Ethernet SM (32R1866)",
        Selected: true,
    }];
    $scope.datacenters = [{
        Name: "DC2",
        Selected: true,
    }, {
        Name: "DC4",
        Selected: true,
    }];
    $scope.environments = [{
        Name: "Prod",
        Selected: true,
    }, {
        Name: "Dev",
        Selected: true,
    }, {
        Name: "Test",
        Selected: true,
    }];
    $scope.results = [{
    	id: 243,
    	name: 'HP ProLiant DL 360 G6',
    	sn: 'DA34FD1X0L',
    	barcode: '1046_CD'
    }, {
    	id: 43,
    	name: 'IBM BladeCenter HS21',
    	sn: 'AWCK89AD9',
    	barcode: '74516_A'
    }, {
    	id: 134,
    	name: 'IBM Ethernet SM (32R1866)',
    	sn: 'ADW891AD02',
    	barcode: '44213_F'
    }]
    $scope.checkAll = function (modelName, checked) {
        angular.forEach($scope[modelName], function (item) {
            item.Selected = checked;
        });
    };
    $scope.preventClose = function(event) { event.stopPropagation(); };
}]);

ang_controllers.controller('mainCtrl', ['$scope', '$routeParams', function ($scope, $routeParams) {

}]);

ang_controllers.controller('leftMenuCtrl', ['$http', '$scope', '$routeParams', function ($http, $scope, $routeParams) {
    $scope.leftMenu = {
        "Stash": {
            "envs": ['prod', 'test', 'dev'],
            "show": true,
        },
        "Allegro": {
            "envs": ['prod', 'test', 'dev'],
        },
        "Agito": {
            "envs": ['prod', 'test', 'dev'],
        },
    }
    $scope.displaySubMenu = function (menu) {
        Object.keys($scope.leftMenu).forEach(function (service) {
            $scope.leftMenu[service].show = false;
        })
        menu.show = true;
    }
    $http({method: 'POST', url: 'http://127.0.0.1:8000/scrooge/menu/services'}).
    success(function(data, status, headers, config) {
        console.log(status)
    }).
    error(function(data, status, headers, config) {
        console.log(status)
    });
}]);

var ButtonsCtrl = function ($scope) {

};

ang_controllers.controller('cardCosts', ['$scope', '$routeParams', function ($scope, $routeParams) {
    $scope.lockedCostData = []
    $scope.choosenYears = []
    $scope.choosenQuarters = []
    $scope.costs = [{
        name: "Microsofct license",
        price: "1 245zł",
        color: "#ff0000",
        years: {
            '2015': {
                'quarter_1': {
                    'january': 84,
                    'february': 53,
                    'march': 76
                 },
                'quarter_2': {
                    'april': 61,
                    'may': 65,
                    'june': 84
                 },
                'quarter_3': {
                    'july': 35,
                    'august': 52,
                    'september': 14
                 },
                'quarter_4': {
                    'obctober': 121,
                    'november': 124,
                    'december': 173
                 }
            },
            '2016': {
                'quarter_1': {
                    'january': 153,
                    'february': 175,
                    'march': 178
                 },
                'quarter_2': {
                    'april': 211,
                    'may': 302,
                    'june': 512
                 },
                'quarter_3': {
                    'july': 932,
                    'august': 1015,
                    'september': 185
                 },
                'quarter_4': {
                    'obctober': 193,
                    'november': 102,
                    'december': 195
                 }
            },
            '2017': {
                'quarter_1': {
                    'january': 434,
                    'february': 454,
                    'march': 644
                 },
                'quarter_2': {
                    'april': 64,
                    'may': 64,
                    'june': 64
                 },
                'quarter_3': {
                    'july': 75,
                    'august': 84,
                    'september': 54
                 },
                'quarter_4': {
                    'obctober': 81234,
                    'november': 82314,
                    'december': 74144
                 }
            }
        }
    }, {
        name: "Support",
        price: "542zł",
        color: "#00ff00",
        years: {
            '2015': {
                'quarter_1': {
                    'january': 584,
                    'february': 453,
                    'march': 776
                 },
                'quarter_2': {
                    'april': 631,
                    'may': 653,
                    'june': 684
                 },
                'quarter_3': {
                    'july': 735,
                    'august': 852,
                    'september': 814
                 },
                'quarter_4': {
                    'obctober': 1221,
                    'november': 1424,
                    'december': 1773
                 }
            },
            '2016': {
                'quarter_1': {
                    'january': 1563,
                    'february': 1675,
                    'march': 1783
                 },
                'quarter_2': {
                    'april': 2121,
                    'may': 3022,
                    'june': 5112
                 },
                'quarter_3': {
                    'july': 9332,
                    'august': 10415,
                    'september': 18155
                 },
                'quarter_4': {
                    'obctober': 1943,
                    'november': 1042,
                    'december': 195
                 }
            },
            '2017': {
                'quarter_1': {
                    'january': 434,
                    'february': 454,
                    'march': 644
                 },
                'quarter_2': {
                    'april': 644,
                    'may': 644,
                    'june': 644
                 },
                'quarter_3': {
                    'july': 755,
                    'august': 84,
                    'september': 954
                 },
                'quarter_4': {
                    'obctober': 84,
                    'november': 84,
                    'december': 74
                 }
            }
        }
    }, {
        name: "Cloud 1",
        price: "123zł",
        color: "#0000ff",
        years: {
            '2015': {
                'quarter_1': {
                    'january': 5784,
                    'february': 4753,
                    'march': 7756
                 },
                'quarter_2': {
                    'april': 6321,
                    'may': 6532,
                    'june': 6784
                 },
                'quarter_3': {
                    'july': 7325,
                    'august': 8352,
                    'september': 8214
                 },
                'quarter_4': {
                    'obctober': 12121,
                    'november': 14224,
                    'december': 17873
                 }
            },
            '2016': {
                'quarter_1': {
                    'january': 15643,
                    'february': 16775,
                    'march': 17832
                 },
                'quarter_2': {
                    'april': 21211,
                    'may': 30223,
                    'june': 51152
                 },
                'quarter_3': {
                    'july': 94332,
                    'august': 104215,
                    'september': 184155
                 },
                'quarter_4': {
                    'obctober': 194773,
                    'november': 104332,
                    'december': 19445
                 }
            },
            '2017': {
                'quarter_1': {
                    'january': 44234,
                    'february': 54454,
                    'march': 64554
                 },
                'quarter_2': {
                    'april': 64214,
                    'may': 64524,
                    'june': 64544
                 },
                'quarter_3': {
                    'july': 74555,
                    'august': 844,
                    'september': 954
                 },
                'quarter_4': {
                    'obctober': 814,
                    'november': 874,
                    'december': 974
                 }
            }
        }
    }, {
        name: "Cloud 2",
        price: "1 582zł",
        color: "#00ffff",
        years: {
            '2015': {
                'quarter_1': {
                    'january': 5454,
                    'february': 4454,
                    'march': 6314
                 },
                'quarter_2': {
                    'april': 6754,
                    'may': 6854,
                    'june': 6954
                 },
                'quarter_3': {
                    'july': 7254,
                    'august': 8454,
                    'september': 8532
                 },
                'quarter_4': {
                    'obctober': 12643,
                    'november': 14454,
                    'december': 13454
                 }
            },
            '2016': {
                'quarter_1': {
                    'january': 15454,
                    'february': 16454,
                    'march': 17454
                 },
                'quarter_2': {
                    'april': 21454,
                    'may': 30124,
                    'june': 51454
                 },
                'quarter_3': {
                    'july': 94254,
                    'august': 104254,
                    'september': 184254
                 },
                'quarter_4': {
                    'obctober': 194254,
                    'november': 104254,
                    'december': 194454
                 }
            },
            '2017': {
                'quarter_1': {
                    'january': 442354,
                    'february': 544454,
                    'march': 645554
                 },
                'quarter_2': {
                    'april': 645214,
                    'may': 645234,
                    'june': 645144
                 },
                'quarter_3': {
                    'july': 745455,
                    'august': 8454,
                    'september': 9454
                 },
                'quarter_4': {
                    'obctober': 8154,
                    'november': 8754,
                    'december': 9754
                 }
            }
        }
    }, {
        name: "Proxmox",
        price: "559zł",
        color: "#ffff00",
        years: {
            '2015': {
                'quarter_1': {
                    'january': 454,
                    'february': 454,
                    'march': 314
                 },
                'quarter_2': {
                    'april': 754,
                    'may': 854,
                    'june': 954
                 },
                'quarter_3': {
                    'july': 1254,
                    'august': 1454,
                    'september': 1532
                 },
                'quarter_4': {
                    'obctober': 1643,
                    'november': 1454,
                    'december': 1454
                 }
            },
            '2016': {
                'quarter_1': {
                    'january': 1454,
                    'february': 1454,
                    'march': 1454
                 },
                'quarter_2': {
                    'april': 2454,
                    'may': 3124,
                    'june': 5454
                 },
                'quarter_3': {
                    'july': 9454,
                    'august': 10454,
                    'september': 18454
                 },
                'quarter_4': {
                    'obctober': 19454,
                    'november': 10454,
                    'december': 4454
                 }
            },
            '2017': {
                'quarter_1': {
                    'january': 4454,
                    'february': 5454,
                    'march': 6454
                 },
                'quarter_2': {
                    'april': 6454,
                    'may': 6454,
                    'june': 6454
                 },
                'quarter_3': {
                    'july': 7454,
                    'august': 8454,
                    'september': 9454
                 },
                'quarter_4': {
                    'obctober': 8454,
                    'november': 8154,
                    'december': 9754
                 }
            }
        }
    }, {
        name: "Xen",
        price: "842zł",
        color: "#aaff00",
        years: {
            '2015': {
                'quarter_1': {
                    'january': 4454,
                    'february': 3454,
                    'march': 2454
                 },
                'quarter_2': {
                    'april': 4454,
                    'may': 3454,
                    'june': 2454
                 },
                'quarter_3': {
                    'july': 5454,
                    'august': 6454,
                    'september': 7532
                 },
                'quarter_4': {
                    'obctober': 6643,
                    'november': 7454,
                    'december': 4454
                 }
            },
            '2016': {
                'quarter_1': {
                    'january': 7454,
                    'february': 6454,
                    'march': 7454
                 },
                'quarter_2': {
                    'april': 8454,
                    'may': 8124,
                    'june': 15454
                 },
                'quarter_3': {
                    'july': 19454,
                    'august': 22454,
                    'september': 28454
                 },
                'quarter_4': {
                    'obctober': 32454,
                    'november': 44454,
                    'december': 34454
                 }
            },
            '2017': {
                'quarter_1': {
                    'january': 41454,
                    'february': 53454,
                    'march': 62454
                 },
                'quarter_2': {
                    'april': 68454,
                    'may': 64454,
                    'june': 63454
                 },
                'quarter_3': {
                    'july': 78454,
                    'august': 78454,
                    'september': 79454
                 },
                'quarter_4': {
                    'obctober': 85454,
                    'november': 88454,
                    'december': 99454
                 }
            }
        }
    }, {
        name: "Total",
        price: "4 982zł",
        active: true,
        color: "#ffaa00",
        years: {
            '2015': {
                'quarter_1': {
                    'january': 20454,
                    'february': 25454,
                    'march': 23454
                 },
                'quarter_2': {
                    'april': 29454,
                    'may': 31454,
                    'june': 27454
                 },
                'quarter_3': {
                    'july': 29454,
                    'august': 32454,
                    'september': 34454
                 },
                'quarter_4': {
                    'obctober': 35454,
                    'november': 43454,
                    'december': 54454
                 }
            },
            '2016': {
                'quarter_1': {
                    'january': 54454,
                    'february': 58454,
                    'march': 58454
                 },
                'quarter_2': {
                    'april': 57454,
                    'may': 87454,
                    'june': 113454
                 },
                'quarter_3': {
                    'july': 124454,
                    'august': 184454,
                    'september': 188454
                 },
                'quarter_4': {
                    'obctober': 228454,
                    'november': 249454,
                    'december': 244454
                 }
            },
            '2017': {
                'quarter_1': {
                    'january': 321454,
                    'february': 423454,
                    'march': 382454
                 },
                'quarter_2': {
                    'april': 488454,
                    'may': 448454,
                    'june': 437454
                 },
                'quarter_3': {
                    'july': 588454,
                    'august': 688454,
                    'september': 598454
                 },
                'quarter_4': {
                    'obctober': 885454,
                    'november': 678454,
                    'december': 1129454
                 }
            }
        }
    }]
    var isLeapYear = function (year) {
        return ((year % 4 === 0) && (year % 100 !== 0)) || (year % 400 === 0);
    };

    var daysInMonth = function (date) {
        return [31, (isLeapYear(date.getYear()) ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][date.getMonth()];
    };

    $scope.removeFromArray = function(value, array) {
        for (i in array) {
            if (array[i] == value) {
                array.splice(i,1);
                return true
            }
        }
        return false
    }
    $scope.inArray = function(value, array) {
        for (i in array) {
            if (array[i] == value) {
                return true
            }
        }
        return false
    }
    $scope.getEndMonthDate = function(year, month) {
        var asString = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        var monthDayMap = {
            'january': 0,
            'february': 1,
            'march': 2,
            'april': 3,
            'may': 4,
            'june': 5,
            'july': 6,
            'august': 7,
            'september': 8,
            'obctober': 9,
            'november': 10,
            'december': 11
        }

        var endDate = year + '-'
        endDate += asString[monthDayMap[month]] + '-'
        endDate += daysInMonth(new Date(year, monthDayMap[month]))
        endDate += ' 01:00AM'
        return endDate
    }
    var getCurrentChartData = function() {
        $scope.currentCostData = []
        $scope.currentSeriesColor = []
        $scope.costs.forEach(function(scopeCost) {
            if (scopeCost.lock || scopeCost.active || scopeCost.over) {
                currentCostData = []
                angular.forEach(scopeCost.years, function(year_value, year) {
                    if ($scope.inArray(year, $scope.choosenYears)) {
                        angular.forEach(year_value, function(quarter_value, quarter) {
                            if ($scope.inArray(quarter, $scope.choosenQuarters)) {
                                angular.forEach(quarter_value, function(month_value, month) {
                                    currentCostData.push([$scope.getEndMonthDate(year, month), month_value, $scope.getEndMonthDate(year, month)])
                                })
                            }
                        })
                    }
                })
                $scope.currentCostData.push(currentCostData)
                $scope.currentSeriesColor = $scope.currentSeriesColor.concat(scopeCost.color)
            }
        });
    }

    $scope.currentCostData = getCurrentChartData()
    $scope.currentSeriesColor = [$scope.costs[$scope.costs.length -1].color]


    $scope.lockCostData = function (cost) {
        cost.lock = !cost.lock
        getCurrentChartData()
    }

    $scope.overCostData = function (cost) {
        cost.over = !cost.over
        getCurrentChartData()
    }

    $scope.activeCost = function (cost) {
        $scope.costs.forEach(function(scopeCost){
            scopeCost.active = false;
        })
        cost.active = true;
        getCurrentChartData()
    }
    $scope.selectYear = function (year) {
        if ($scope.inArray(year, $scope.choosenYears) == true) {
            $scope.removeFromArray(year, $scope.choosenYears)
        } else {
            $scope.choosenYears = $scope.choosenYears.concat(year)
        }
        getCurrentChartData()
    }
    $scope.selectQuarter = function (quarter) {
        if ($scope.inArray(quarter, $scope.choosenQuarters) == true) {
            $scope.removeFromArray(quarter, $scope.choosenQuarters)
        } else {
            $scope.choosenQuarters = $scope.choosenQuarters.concat(quarter)
        }
        getCurrentChartData()
    }

}]);

ang_controllers.controller('dependencytree', ['$scope', '$routeParams', function ($scope, $routeParams) {

    $scope.tree = {
      "cols" : [
          {"label": "Name", "pattern": "", "type": "string"},
          {"label": "Manager", "pattern": "", "type": "string"},
          {"label": "ToolTip", "pattern": "", "type": "string"}
      ],
      "rows" : [
          {"c": [
              {"v": "1", "f": "Stash" },
              {"v": ""},
              {"v": "service_main"},
          ]},
          {"c": [
              {"v": "2", "f": "Assets"},
              {"v": "1"},
              {"v": "device"}
          ]},
          {"c": [
              {"v": "3", "f": "Hamster"},
              {"v": "1"},
              {"v": "service"}
          ]},
          {"c": [
              {"v": "4", "f": "Cloud"},
              {"v": "1"},
              {"v": "service"}
          ]},
          {"c": [
              {"v": "5", "f": "Open Stack"},
              {"v": "1"},
              {"v": "service"}
          ]},
          {"c": [
              {"v": "6", "f": "Extra Costs"},
              {"v": "1"},
              {"v": "extra_cost"}
          ]},
          {"c": [
              {"v": "7", "f": "Proxmox"},
              {"v": "1"},
              {"v": "service"}
          ]},
          {"c": [
              {"v": "8", "f": "mysql"},
              {"v": "1"},
              {"v": "service"}
          ]},
          {"c": [
              {"v": "12", "f": "Power Consumption"},
              {"v": "1", },
              {"v": "base_cost"}
          ]},
          {"c": [
              {"v": "11", "f": "Power Consumption"},
              {"v": "1", },
              {"v": "base_cost"}
          ]},
          {"c": [
              {"v": "9", "f": "Power Consumption"},
              {"v": "1", },
              {"v": "base_cost"}
          ]},
          {"c": [
              {"v": "10", "f": "Power Consumption"},
              {"v": "1"},
              {"v": "base_cost"}
          ]}
      ]
    }
    $scope.chartObject = {
      "chartType": "OrgChart",
      "displayed": true,
      "containerId": 'treechart',
      "dataTable": $scope.tree,
      "options": {
        "dataSourceInput": "<div>test</div>",
        "annotations": {
            "textStyle": {
                "color":"#ffaaaa",
            },
            "boxStyle": {
              "stroke": '#888',           // Color of the box outline.
              "strokeWidth": "1",           // Thickness of the box outline.
              "rx": "10",                   // x-radius of the corner curvature.
              "ry": "10",                   // y-radius of the corner curvature.
              "gradient": {               // Attributes for linear gradient fill.
                "color1": '#fbf6a7',      // Start color for gradient.
                "color2": '#33b679',      // Finish color for gradient.
                "x1": '0%', "y1": '0%',     // Where on the boundary to start and end the
                "x2": '100%', "y2": '100%', // color1/color2 gradient, relative to the
                "useObjectBoundingBoxUnits": true // If true, the boundary for x1, y1,
              }
            }
          },
        "title": "Sales per month",
        "isStacked": "true",
        "fill": 20,
        "displayExactValues": true,
        "allowCollapse":true,
      },
      "formatters": {}
    }

    var app = angular.module('myApp', [ 'googlechart' ]);

    var chart1 = {};
        chart1.type = "PieChart";
            chart1.data = [
       ['Component', 'cost'],
       ['Software', 50000],
       ['Hardware', 80000]
    ];
    chart1.data.push(['Services',20000]);
    chart1.options = {
        width: 400,
        height: 300,
        is3D: true,
    };

    chart1.formatters = {
        number : [{
            columnNum: 1,
            pattern: "$ #,##0.00"
        }]
    };

    $scope.chart = chart1;

    $scope.aa=1*$scope.chart.data[1][1];
    $scope.bb=1*$scope.chart.data[2][1];
    $scope.cc=1*$scope.chart.data[3][1];

}]);
    //    [[[1, 2],[3,5.12],[5,13.1],[7,33.6],[9,85.9],[11,219.9]]],
