var gulp = require('gulp'),
	coffeelint = require('gulp-coffeelint'),
	notify = require('gulp-notify'),
	concat = require('gulp-concat'),
	// docco = require('gulp-docco'),
	coffee = require('gulp-coffee'),
	deleteLines = require('gulp-delete-lines');

gulp.task('compile', function(){
	gulp.src([
		'../../../../nh_eobs_mobile/static/dev/coffee/src/*.coffee',
		'src/*.coffee'
	])
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(deleteLines({
		'filters': [
			/### istanbul/i
		]
	}))
	.pipe(coffee({bare: true}))
	.pipe(concat('nhlib.js'))
	.pipe(gulp.dest('../../src/js'))
});

gulp.task('pycharm_test', function(){
	gulp.src([
		'../../../../nh_eobs_mobile/static/dev/coffee/src/*.coffee',
		'src/*.coffee'
	])
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(coffee({bare: true}))
	.pipe(gulp.dest('tests/src'));
});

//
// gulp.task('docs', function(){
// 	gulp.src(['src/*.coffee'])
// 	.pipe(deleteLines({
// 			'filters': [
// 				/### istanbul/i
// 			]
// 		}))
// 	.pipe(docco())
// 	.pipe(gulp.dest('docs'))
// });

gulp.task('default', ['compile']);