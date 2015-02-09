module.exports = function(grunt) {
  'use strict';

  grunt.initConfig({
    jshint: {
        all: [
            'Gruntfile.js',
            'src/ralph_scrooge/static/scrooge/app/*',
            'src/ralph_scrooge/static/scrooge/js/scrooge.js',
            'src/ralph_scrooge/static/scrooge/js/table_fixed_header.js'
        ],
        options: {
            'node': true,
            globals: {
                'document': false,
                'window': false,
                '$': false,
                'angular': false,
                'describe': false,
                'beforeEach': false,
                'it': false,
                'inject': false,
                'expect': false
            }
        },
    },
    karma: {
        unit: {
            configFile: 'karma.conf.js'
        }
    },
    copy: {
        main: {
            files: [
                {
                    expand: true,
                    flatten: true,
                    src: [
                        'bower_components/angular/angular.min.js',
                        'bower_components/angular/angular.min.js.map',
                        'bower_components/angular-animate/angular-animate.min.js',
                        'bower_components/angular-animate/angular-animate.min.js.map',
                        'bower_components/angular-cookies/angular-cookies.min.js',
                        'bower_components/angular-cookies/angular-cookies.min.js.map',
                        'bower_components/angular-mocks/angular-mocks.js',
                        'bower_components/angular-resource/angular-resource.min.js',
                        'bower_components/angular-resource/angular-resource.min.js.map',
                        'bower_components/angular-route/angular-route.min.js',
                        'bower_components/angular-route/angular-route.min.js.map',
                        'bower_components/bootstrap/dist/js/bootstrap.min.js',
                        'bower_components/bootstrap-table/dist/bootstrap-table.min.js',
                        'bower_components/jquery/dist/jquery.min.js',
                        'bower_components/jquery/dist/jquery.min.js.map',
                        'bower_components/multiple-select/jquery.multiple.select.js',
                        'bower_components/ng-scrollbar/dist/ng-scrollbar.min.js',
                    ],
                    dest: 'src/ralph_scrooge/static/vendor',
                    filter: 'isFile'
                },
                {
                    expand: true,
                    flatten: true,
                    src: [
                        'bower_components/bootstrap/dist/css/bootstrap.min.css',
                        'bower_components/bootstrap/dist/css/bootstrap-theme.min.css',
                        'bower_components/bootstrap-table/dist/bootstrap-table.min.css',
                        'bower_components/multiple-select/multiple-select.css',
                        'bower_components/ng-scrollbar/dist/ng-scrollbar.css',
                        'bower_components/font-awesome/css/font-awesome.min.css'
                    ],
                    dest: 'src/ralph_scrooge/static/scrooge/css',
                    filter: 'isFile'
                },
                {
                    expand: true,
                    flatten: true,
                    src: [
                        'bower_components/bootstrap/dist/fonts/*',
                        'bower_components/font-awesome/fonts/*',
                    ],
                    dest: 'src/ralph_scrooge/static/scrooge/fonts',
                    filter: 'isFile'
                },
            ],
        },
    },
  });

  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-karma');
  grunt.loadNpmTasks('grunt-contrib-copy');
};
