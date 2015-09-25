module.exports = function(config) {

    if (!process.env.SAUCE_USERNAME || !process.env.SAUCE_ACCESS_KEY) {
        console.log('Make sure the SAUCE_USERNAME and SAUCE_ACCESS_KEY environment variables are set.');
        process.exit(1);
    }

    var customLaunchers = {
        'SL_Chrome': {
            base: 'SauceLabs',
            browserName: 'chrome',
            timeZone: 'London'
        },
        'SL_Firefox': {
            base: 'SauceLabs',
            browserName: 'firefox',
            timeZone: 'London'
        },
        'SL_Mobile_Safari': {
            base: 'SauceLabs',
            browserName: 'iphone',
            version: '8.0',
            timeZone: 'London',
            deviceName: 'iPad 2',
            deviceOrientation: 'portrait'
        }
    };

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

        //hostname: 'localhost',
        port: 9876,
        colors: true,
        reporters: ['progress', 'saucelabs'],

        preprocessors: {
            'tests/src/*.js': ['coverage']
        },
        sauceLabs:{
            testName: 'NHMobile',
            recordScreenshots: true,
            connectOptions: {
                port: 5757,
                logfile: 'sauce_connect.log',
                username: process.env.SAUCE_USERNAME,
                accessKey: process.env.SAUCE_ACCESS_KEY
            }
        },
        browserNoActivityTimeout: 60000,
        captureTimeout: 120000,
        customLaunchers: customLaunchers,
        browsers: Object.keys(customLaunchers),
        autoWatch: false,
        singleRun: true,

        frameworks: ['jasmine-ajax', 'jasmine'],

        plugins: [
            'karma-jasmine',
            'karma-jasmine-ajax',
            'karma-junit-reporter',
            'karma-phantomjs-launcher',
            'karma-coverage',
            'karma-nyan-reporter',
            'karma-html-reporter',
            'karma-sauce-launcher'
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