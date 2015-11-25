var gulp = require('gulp'),
	less = require('gulp-less'),
	bower = require('gulp-bower-files'),
	handlebars = require('gulp-compile-handlebars'),
	rename = require('gulp-rename'),
	del = require('del'),
	data = require('./dev/data.json');

gulp.task('compileLESS', function(){
	gulp.src('./dev/less/style.less')
	.pipe(less())
	.pipe(gulp.dest('./mockup/src/css'));
});

gulp.task('moveJS', function(){
	gulp.src('./dev/js/main.js')
	.pipe(gulp.dest('./mockup/src/js'));
})

gulp.task("moveBowerFiles", function(){
    bower()
    .pipe(gulp.dest("./mockup"));
});

gulp.task("compileHandleBars", function(){
	var templateData = data, // find way to read data.json
	options = {
		batch: ['./dev/templates']
	}
	return gulp.src('./dev/templates/index.hbs')
	.pipe(handlebars(templateData, options))
	.pipe(rename('index.html'))
	.pipe(gulp.dest('mockup'));
});

gulp.task('build', ['compileLESS', 'moveJS', 'moveBowerFiles', 'compileHandleBars']);