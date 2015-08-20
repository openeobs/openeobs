var gulp = require('gulp'),
	coffeelint = require('gulp-coffeelint'),
	karma = require('gulp-karma'),
	notify = require('gulp-notify'),
	concat = require('gulp-concat'),
	docco = require('gulp-docco'),
	coffee = require('gulp-coffee'),
	deleteLines = require('gulp-delete-lines');

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
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(coffee({bare: true}))
	.pipe(gulp.dest('tests/src'))
	gulp.src(['tests/src/*.js', 'tests/lib/test_routes.js', 'tests/spec/*.js'])
	.pipe(karma({
		configFile: 'karma.conf.js',
		action: 'run'
	}))
});

gulp.task('test_reports', function(){
	gulp.src(['src/*.coffee'])
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(coffee({bare: true}))
	.pipe(gulp.dest('tests/src'))
	gulp.src(['tests/src/*.js', 'tests/lib/test_routes.js', 'tests/spec/*.js'])
	.pipe(karma({
		configFile: 'karma.conf.js',
		action: 'run'
	}))
});

gulp.task('pycharm_test', function(){
	gulp.src(['src/*.coffee'])
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(coffee({bare: true}))
	.pipe(gulp.dest('tests/src'))
	//gulp.src(['tests/src/*.js', 'tests/lib/test_routes.js', 'tests/spec/*.js'])
	//.pipe(karma({
	//	configFile: 'karma.conf.js',
	//	action: 'run'
	//}))
});

gulp.task('docs', function(){
	gulp.src(['src/*.coffee'])
	.pipe(deleteLines({
			'filters': [
				/### istanbul/i
			]
		}))
	.pipe(docco())
	.pipe(gulp.dest('docs'))
})

gulp.task('default', ['compile']);