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
		    'tests/spec/events.spec.js'
        ],

        exclude: [],

        hostname: 'localhost',
        port: 9876,

        reporters: ['nyan', 'html', 'coverage'],

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

        htmlReporter: {
            outputDir: 'karma_html',
            templatePath: null,
            focusOnFailures: false,
            namedFiles: false,
            pageTitle: null,
            urlFriendlyName: false,
            reportName: 'report-summary-filename',
            preserveDescribeNesting: true
        }

    })
}