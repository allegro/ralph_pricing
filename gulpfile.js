var gulp = require('gulp');
const del = require('del');
const typescript = require('gulp-typescript');
const tscConfig = require('./tsconfig.json');
const sourcemaps = require('gulp-sourcemaps');
const rename = require('gulp-rename');

const mediaPath = 'src/ralph_scrooge/media/'
const appPath = mediaPath + 'scrooge/'


gulp.task('clean', function () {
  return del(appPath + 'dist/**/*');
});


gulp.task('clean_libs', function () {
  return del(appPath + 'lib/**/*');
});


gulp.task('compile', ['clean'], function () {
   return gulp
    .src(['typings/browser.d.ts', appPath + 'appts/**/*.ts'])
    .pipe(sourcemaps.init())
    .pipe(typescript(tscConfig.compilerOptions))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(appPath + 'dist'));
});


gulp.task('tslint', function() {
  var tslint = require('gulp-tslint');
  return gulp.src(appPath + 'appts/**/*.ts')
    .pipe(tslint())
    .pipe(tslint.report('verbose'));
});


gulp.task("libs", ['clean_libs'], function() {
    return gulp.src([
        'es6-shim/es6-shim.min.js',
        'systemjs/dist/system-polyfills.js',
        'systemjs/dist/system.js',
        'reflect-metadata/Reflect.js',
        'rxjs/util/isFunction.js',
        'rxjs/Observer.js',
        'rxjs/util/isArray.js',
        'rxjs/util/isObject.js',
        'rxjs/util/tryCatch.js',
        'rxjs/util/errorObject.js',
        'rxjs/util/UnsubscriptionError.js',
        'rxjs/Observable.js',
        'rxjs/Subject.js',
        'rxjs/observable/PromiseObservable.js',
        'rxjs/operator/toPromise.js',
        'rxjs/add/observable/throw.js',
        'rxjs/observable/throw.js',
        'rxjs/add/operator/catch.js',
        'rxjs/add/operator/map.js',
        'rxjs/Subscriber.js',
        'rxjs/Subscription.js',
        'rxjs/SubjectSubscription.js',
        'rxjs/symbol/rxSubscriber.js',
        'rxjs/util/ObjectUnsubscribedError.js',
        'rxjs/util/throwError.js',
        'rxjs/symbol/observable.js',
        'rxjs/util/root.js',
        'rxjs/observable/ErrorObservable.js',
        'rxjs/util/toSubscriber.js',
        'rxjs/operator/catch.js',
        'rxjs/operator/map.js',
        'zone.js/dist/zone.min.js',
        'raven-js/dist/raven.min.js',
        'zone.js/dist/zone.min.js',
        '@angular/common/common.umd.js',
        '@angular/compiler/compiler.umd.js',
        '@angular/core/core.umd.js',
        '@angular/http/http.umd.js',
        '@angular/platform-browser/platform-browser.umd.js',
        '@angular/platform-browser-dynamic/platform-browser-dynamic.umd.js',
        '@angular/router-deprecated/router-deprecated.umd.js',
        '@angular/upgrade/upgrade.umd.js',
    ], {cwd: "node_modules/**"}) /* Glob required here. */
    .pipe(gulp.dest(appPath + "lib/"));
});


gulp.task("dev_libs", function() {
    return gulp.src([
        'jasmine-core/lib/jasmine-core/jasmine.css',
        'jasmine-core/lib/jasmine-core/jasmine.js',
        'jasmine-core/lib/jasmine-core/jasmine-html.js',
        'jasmine-core/lib/jasmine-core/boot.js'
    ], {cwd: "node_modules/**"}) /* Glob required here. */
    .pipe(gulp.dest(appPath + "lib/"));
});

gulp.task("swagger", ['clean_swagger'], function() {
    return gulp.src([
        'css/**',
        'fonts/**',
        'images/**',
        'lang/**',
        'lib/**',
        'swagger-ui.js',
        'swagger-ui.min.js',
        'o2c.html',
    ], {cwd: "node_modules/swagger-ui/dist/**"}) /* Glob required here. */
    .pipe(gulp.dest(mediaPath + "swagger/"));
});

gulp.task('clean_swagger', function () {
  return del(mediaPath + 'swagger/**');
});

gulp.task('default', function() {
    gulp.start('compile', 'libs', 'swagger');
});
