module.exports = function(config) {
    config.set({
        basePath: '',

        files: [
            'tests/src/*js',
            'tests/lib/helpers.js',
            'tests/lib/test_routes.js',
            'tests/spec/conversion.spec.js',
		    'tests/spec/network.spec.js',
		    'tests/spec/patient_info.spec.js',
		    'tests/spec/utility.spec.js',
            'tests/spec/standin.spec.js',
            'tests/spec/form.spec.js',
		    'tests/spec/events.spec.js'
        ],

        exclude: [],

        hostname: 'localhost',
        port: 9876,

        reporters: ['progress'],

        preprocessors: {
            'tests/src/*.js': ['coverage']
        },

        autoWatch: false,
        singleRun: true,

        frameworks: ['jasmine-ajax', 'jasmine'],

        customLaunchers: {
            ChromeTravis: {
                base: 'Chrome',
                flags: [ '--no-sandbox' ]
            }
        },

        browsers: ['ChromeTravis'],

        plugins: [
            'karma-jasmine',
            'karma-jasmine-ajax',
            'karma-junit-reporter',
            'karma-phantomjs-launcher',
            'karma-chrome-launcher',
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
          type : 'text'
        },
    })
}