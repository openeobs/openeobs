var gulp = require('gulp'),
    uglify = require('gulp-uglify'),
    concat = require('gulp-concat');

gulp.task('build_observation_js', function(){
    gulp.src(['../js/gcs-score.js', '../js/modals.js', '../js/observation.js','../js/submission.js','../js/validation.js'])
        .pipe(uglify())
        .pipe(concat('observation.js'))
        .pipe(gulp.dest('../../src/js'))
});

gulp.task('build_patientgraph_js', function(){
    gulp.src(['../js/graph-setup.js','../js/graph-util.js','../js/graph-drawing.js','../js/interaction.js','../js/graph-ews.js','../js/modals.js'])
        .pipe(uglify())
        .pipe(concat('patient_graph.js'))
        .pipe(gulp.dest('../../src/js'))
});
