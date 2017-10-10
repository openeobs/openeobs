module.exports = function (config) {

    if (!process.env.SAUCE_USERNAME || !process.env.SAUCE_ACCESS_KEY) {
        console.log('Make sure the SAUCE_USERNAME and SAUCE_ACCESS_KEY environment variables are set.');
        process.exit(1);
    }

    var customLaunchers = {
        'SL_Android_Chrome': {
            base: 'SauceLabs',
            browserName: 'Browser',
            appiumVersion: '1.6.4',
            deviceName: 'Android Emulator',
            deviceOrientation: 'portrait',
            platformVersion: '5.1',
            platformName: 'Android',
            timeZone: 'Universal'
        },
        'SL_Windows_Chrome': {
            base: 'SauceLabs',
            browserName: 'chrome',
            version: '50.0',
            platform: 'Windows 10',
            timeZone: 'Universal'
        }
    };

    config.set({
        basePath: '',

        files: [
            'tests/src/*.js',
            'tests/lib/*.js',
            'tests/spec/*.js'
        ],

        exclude: [],

        //hostname: 'localhost',
        port: 9876,

        reporters: ['dots', 'saucelabs'],

        preprocessors: {
            'tests/src/*.js': ['coverage']
        },
        sauceLabs:{
            testName: 'NHGraphLib - #' + process.env.TRAVIS_BUILD_NUMBER + '.' + process.env.TRAVIS_BUILD_ID,
            recordScreenshots: true,
            startConnect: false,
            maxDuration: 240,
            tunnelIdentifier: process.env.TRAVIS_JOB_NUMBER,
            connectOptions: {
                port: 5757,
                logfile: 'sauce_connect.log',
                username: process.env.SAUCE_USERNAME,
                accessKey: process.env.SAUCE_ACCESS_KEY
            },

        },
        customLaunchers: customLaunchers,
        browsers: Object.keys(customLaunchers),
        autoWatch: false,
        singleRun: true,
        frameworks: ['jasmine'],
        plugins: [
            'karma-jasmine',
            'karma-junit-reporter',
            'karma-phantomjs-launcher',
            'karma-chrome-launcher',
            'karma-firefox-launcher',
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
            type: 'html',
            dir: 'coverage/'
        }
    })
}