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
                        'bower_components/**/*.min.js',
                        'bower_components/**/*.min.js.map',
                        'bower_components/angular-mocks/angular-mocks.js',
                        'bower_components/multiple-select/jquery.multiple.select.js',
                    ],
                    dest: 'src/ralph_scrooge/static/vendor',
                    filter: 'isFile'
                },
                {
                    expand: true,
                    flatten: true,
                    src: [
                        'bower_components/**/*.min.css',
                        'bower_components/multiple-select/multiple-select.css',
                        'bower_components/ng-scrollbar/dist/ng-scrollbar.css',
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
