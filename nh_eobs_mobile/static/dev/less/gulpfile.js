var gulp = require('gulp'),
	less = require('gulp-less'),
	util = require('gulp-util');

gulp.task('compileLESS', function(){
	gulp.src('src/compile.less')
	.pipe(less().on('error', util.log))
	.pipe(gulp.dest('style/'));
});