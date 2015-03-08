var gulp = require('gulp'),
	coffeelint = require('gulp-coffeelint'),
	jasmine = require('gulp-jasmine2-phantomjs'),
	notify = require('gulp-notify'),
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

gulp.task('test', function(){
	gulp.src(['src/*.coffee'])
	.pipe(coffee({bare: true}))
	.pipe(gulp.dest('tests/src'))

	gulp.src('tests/specRunner1.3.html')
	.pipe(jasmine())
})

gulp.task('default', ['compile']);