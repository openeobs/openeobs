module.exports = function(config) {
    config.set({
        basePath: '',

        files: [
            '../../../../nh_eobs_mobile/static/dev/coffee/tests/lib/helpers.js',
            '../../../../nh_eobs_mobile/static/dev/coffee/tests/lib/test_routes.js',
            'tests/src/*js',
            'tests/spec/*.spec.js',
            '../../../../nh_eobs_mobile/static/dev/coffee/tests/spec/*.spec.js'
        ],

        exclude: [],

        hostname: 'localhost',
        port: 9876,

        reporters: ['nyan', 'coverage'],

        preprocessors: {
            'tests/src/*.js': ['coverage']
        },

        autoWatch: false,
        singleRun: true,

        frameworks: ['jasmine-ajax', 'jasmine'],

        browsers: ['PhantomJS'],

        plugins: [
            'karma-jasmine',
            'karma-jasmine-ajax',
            'karma-junit-reporter',
            'karma-phantomjs-launcher',
            'karma-coverage',
            'karma-nyan-reporter',
            'karma-html-reporter'
        ],

        junitReporter: {
            outputFile: 'unit.xml',
            suite: 'unit'
        },

        // optionally, configure the reporter
        coverageReporter: {
          type : 'html',
          dir : 'coverage/'
        },
    });
};