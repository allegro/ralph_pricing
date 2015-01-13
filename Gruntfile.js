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
            }
        }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.registerTask('default', 'jshint');

};
