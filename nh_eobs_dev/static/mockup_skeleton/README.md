# Mockup Skeleton
A simple set of files to get things up and running easy

## Dependencies
The skeleton uses Node and NPM so for things to work you need to install these

## Getting started
Open a terminal window in the root folder (the one this read me is in) and run:
`npm install`
This will then go off and download the different node packages this skeleton uses, one of which is Bower. 

The next step is to use Bower to install the various JavaScript libraries the mockup will use via:
`bower install`
This will install the files in the components folder (which the example template is prelinked to)

Any dependencies you want to add to the project should be added to these files, doing so will allow others to follow the same steps to get started with your code.

## Building the mockup
The idea behind the mockup skeleton is that you only need to concern yourself with 4 things:
 - LESS for styling
 - JavaScript for interaction
 - HTML (and handlebars) for component based markup
 - the data.json file where the data used to power the mockup will sit
 
The mockup is build using gulp, a JavaScript powered build tool. 
To run the build script just type `gulp build` into the terminal and it will compile the LESS to CSS, Move the JS into the mockup, mash the templates and the data.json files into a finished mockup and run some analysis on potential issues that may arise when showing on different browsers.

You can add build phases via the gulpfile.js file if you wish