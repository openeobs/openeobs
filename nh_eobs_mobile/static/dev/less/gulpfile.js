var gulp = require('gulp'),
	less = require('gulp-less'),
	util = require('gulp-util'),
	del = require('del'),
	kss = require('gulp-kss');

gulp.task('compileLESS', function(){
	gulp.src('src/compile.less')
	.pipe(less().on('error', util.log))
	.pipe(gulp.dest('style/'));
});

gulp.task('Styleguide', function(){
	del(['styleguide/**']);
	gulp.src(['src/nav.less',
		'src/modal.less',
		'src/button.less',
		'src/form.less',
		'src/list.less'])
	.pipe(kss({
		overview: 'src/styleguide_overview.md',
		templateDirectory: 'src/templates'
	}))
	.pipe(gulp.dest('styleguide/'));

	gulp.src(['src/compile.less'])
	.pipe(less().on('error', util.log))
	.pipe(gulp.dest('styleguide/public'));
});

gulp.task('default', ['compileLESS']);