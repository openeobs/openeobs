module.exports = function(config) {
    config.set({
        basePath: '',

        files: [
            'tests/src/*js',
            'tests/lib/test_routes.js',
            'tests/spec/*.spec.js'
        ],

        exclude: [
        ],

        reporters: ['html', 'coverage'],

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