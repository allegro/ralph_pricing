// Karma configuration
// Generated on Tue Jan 13 2015 12:09:28 GMT+0000 (UTC)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
        'src/ralph_scrooge/static/vendor/jquery/dist/jquery.min.js',
        'src/ralph_scrooge/static/vendor/multiple-select/jquery.multiple.select.js',
        'src/ralph_scrooge/static/vendor/angular/angular.min.js',
        'src/ralph_scrooge/static/vendor/angular-mocks/angular-mocks.js',
        'src/ralph_scrooge/static/vendor/angular-animate/angular-animate.min.js',
        'src/ralph_scrooge/static/vendor/angular-resource/angular-resource.min.js',
        'src/ralph_scrooge/static/vendor/angular-route/angular-route.min.js',
        'src/ralph_scrooge/static/vendor/angular-cookies/angular-cookies.min.js',
        'src/ralph_scrooge/static/vendor/ng-scrollbar/dist/ng-scrollbar.min.js',
        'src/ralph_scrooge/static/vendor/bootstrap/dist/js/bootstrap.min.js',
        'src/ralph_scrooge/static/vendor/bootstrap-table/dist/bootstrap-table.min.js',

        'src/ralph_scrooge/static/scrooge/js/ui-bootstrap-tpls-0.10.0.min.js',
        'src/ralph_scrooge/static/scrooge/js/loading-bar.js',
        'src/ralph_scrooge/static/scrooge/js/scrooge.js',

        'src/ralph_scrooge/static/scrooge/app/**/*.js',
        'src/ralph_scrooge/static/scrooge/app/tests/**/*.js'
    ],


    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Firefox'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: true
  });
};
