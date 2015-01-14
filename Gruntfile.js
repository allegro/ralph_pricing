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
        }
    },
    karma: {
        unit: {
            configFile: 'karma.conf.js'
        }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-karma');

  grunt.registerTask('default', ['jshint', 'karma']);
};
