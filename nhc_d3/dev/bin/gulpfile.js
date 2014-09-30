var gulp = require('gulp'),
    uglify = require('gulp-uglify'),
    concat = require('gulp-concat');

gulp.task('build_patient_graph_for_mobile_desktop', function(){
    gulp.src(['../js/graph_lib_object_start.js', '../js/graph-setup.js','../js/graph-draw.js', '../js/graph-util.js', '../js/graph_lib_object_end.js'])
        .pipe(concat('patient_graph.js'))
        //.pipe(uglify({output: {beautify: true}}))
        .pipe(gulp.dest('../../static/src/js'))
});

gulp.task('build_patient_graph_for_reports', function(){
    gulp.src(['../js/graph_lib_object_start.js', '../js/graph-setup.js','../js/graph-util.js','../js/graph-draw.js', '../js/graph_lib_object_end.js'])
        .pipe(concat('report_graph.js'))
        .pipe(uglify({output: {beautify: true}}))
        .pipe(gulp.dest('../../static/src/js'))
});
