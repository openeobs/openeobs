var gulp = require('gulp'),
	coffeelint = require('gulp-coffeelint'),
	jasmine = require('gulp-jasmine-phantom'),
	notify = require('gulp-notify'),
	uglify = require('gulp-uglify'),
	concat = require('gulp-concat'),
	coffee = require('gulp-coffee');

gulp.task('compile', function(){
	gulp.src(['src/*.coffee'])
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(coffee({bare: true}))
	.pipe(concat('nhlib.js'))
	.pipe(gulp.dest('../../src/js'))
});

gulp.task('default', ['compile']);