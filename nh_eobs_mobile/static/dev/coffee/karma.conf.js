module.exports = function(config) {
    config.set({
        basePath: '',

        files: [
        ],

        exclude: [
        ],

        reporters: ['progress', 'coverage'],

        preprocessors: {
            'tests/src/*.js': ['coverage']
        },

        autoWatch: false,
        singleRun: true,

        frameworks: ['jasmine'],

        browsers: ['PhantomJS'],

        plugins: [
            'karma-jasmine',
            'karma-junit-reporter',
            'karma-phantomjs-launcher',
            'karma-coverage'
        ],

        junitReporter: {
            outputFile: 'unit.xml',
            suite: 'unit'
        },

        // optionally, configure the reporter
        coverageReporter: {
          type : 'html',
          dir : 'coverage/'
        }

    })
}