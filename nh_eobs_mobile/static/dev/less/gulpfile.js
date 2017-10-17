var gulp = require('gulp'),
	less = require('gulp-less'),
	util = require('gulp-util'),
	del = require('del'),
	kss = require('gulp-kss'),
	flatten = require('gulp-flatten');

gulp.task('compileLESS', function(){
	gulp.src('src/nhc.less')
	.pipe(less().on('error', util.log))
	.pipe(gulp.dest('../../src/css/'));
});

gulp.task('Styleguide', function(){
	del(['styleguide/**']);
	gulp.src([
		'src/general.less',
		'src/modal.less',
		'src/alert.less',
		'src/button.less',
		'src/form.less',
		'src/list.less',
		'src/data_visualisation.less',
		'src/type.less'])
	.pipe(kss({
		overview: 'src/styleguide_overview.md',
		templateDirectory: 'src/templates'
	}))
	.pipe(gulp.dest('styleguide/'));

	gulp.src(['src/nhc.less'])
	.pipe(less().on('error', util.log))
	.pipe(gulp.dest('styleguide/public'));

	gulp.src('src/templates/public/**')
		.pipe(flatten())
		.pipe(gulp.dest('styleguide/public'))
});

gulp.task('default', ['compileLESS']);