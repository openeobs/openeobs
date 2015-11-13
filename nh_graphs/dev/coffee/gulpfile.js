var gulp = require('gulp'),
coffeelint = require('gulp-coffeelint'),
karma = require('gulp-karma'),
notify = require('gulp-notify'),
concat = require('gulp-concat'),
docco = require('gulp-docco'),
coffee = require('gulp-coffee'),
sauceConnectLauncher = require('sauce-connect-launcher');

gulp.task('sauce_start', function() {
	sauceConnectLauncher({
		username: 'neovahealth',
		accessKey: 'b7964b4f-b0e7-44ee-81e3-883c3ee47652'
	}, function (err, sauceConnectProcess) {
		if (err) {
			console.error(err.message);
			return;
		}
		console.log("Sauce Connect ready");
	});
});

gulp.task('sauce_stop', function() {
	sauceConnectLauncher({
		username: 'neovahealth',
		accessKey: 'b7964b4f-b0e7-44ee-81e3-883c3ee47652'
	}, function (err, sauceConnectProcess) {
		sauceConnectProcess.close(function () {
			console.log("Closed Sauce Connect process");
		})
	});
});

var Server = require('karma').Server;

gulp.task('compile', function(){
	gulp.src(['src/*.coffee'])
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(coffee({bare: true}))
	.pipe(concat('nh_graphlib.js'))
	.pipe(gulp.dest('../../static/src/js'))
});

gulp.task('karma', function (done) {
  new Server({
    configFile: __dirname + '/karma.conf.js',
    singleRun: true
  }, done).start()
});

gulp.task('test', function(){
	gulp.src(['src/*.coffee'])
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(coffee({bare: true}))
	.pipe(gulp.dest('tests/src'))

	gulp.src(['tests/src/*.js', 'tests/lib/*.js', 'tests/spec/*.js'])
	.pipe(karma({
		configFile: 'karma.conf.js',
		action: 'run'
	}))
});

gulp.task('docs', function(){
	gulp.src(['src/*.coffee'])
	.pipe(docco())
	.pipe(gulp.dest('docs'))
})

gulp.task('pycharm_test_compile', function(){

	// Compile source coffee
	gulp.src(['src/*.coffee'])
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(coffee({bare: true}))
	.pipe(gulp.dest('tests/src'));

});

gulp.task('default', ['compile']);
gulp.task('all',['pycharm_test_compile','karma']);