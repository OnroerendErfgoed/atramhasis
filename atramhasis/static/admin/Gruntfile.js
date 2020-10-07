/*jshint node:true*/
module.exports = function (grunt) {
  var path = require('path');

  grunt.initConfig({
    dojo: {
      dist: {
        options: {
          dojo: path.join('node_modules', 'dojo', 'dojo.js'),
          dojoConfig: path.join('src', 'dojoConfig.js'),
          profile: path.join('profiles', 'atramhasis.profile.js'),
          releaseDir: path.join('..', 'dist'),
          basePath: path.join(__dirname, 'node_modules')
        }
      }
    },
    copy: {
      config: {
        options: {
          processContent: function (content) {
            return content.replace(/isDebug:\s+(true|1),?\s+/, '');
          }
        },
        files: [{
          src: path.join('src', 'dojoConfig.js'),
          dest: path.join('dist', 'dojoConfig.js')
        }]
      }
    },
    clean: {
      dist: {
        files: [{
          dot: true,
          src: [
            'dist'
          ]
        }]
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-dojo');

  grunt.config('copy.fa', {
    files: [
      {
        cwd: 'src/font-awesome/fonts',
        src: '**/*',
        dest: 'dist/font-awesome/fonts',
        expand: true
      }
    ]
  });

  grunt.registerTask('build', [ 'clean', 'dojo:dist', 'copy', 'copy:fa']);
};
