Open-eObs is an open source project and is open to contributions from the 
community via the creation of issues and pull requests.

It's recommended before starting work on new functionality that you create an issue
to communicate your need to the team as we may already have started working on this.

There are a number of standards that the core development team hold themselves
to that we ask any contributors to honour, these are explained in the 
pull request and issue templates.

# Contributing Code
When contributing code we ask that you follow the steps in our pull request template. 
These steps will be used by the development team to work through the assessment
of the code you're contributing and helps to ease communication during review.

## Getting the code
To get the code you can fork this repo by pressing the `Fork` button on Github 
(this requires you to be signed in). This will then allow you to work on your own version
of Open-eObs.

It's recommended that you work on your own branch (not `master` or `develop`). This
is so you can easily merge any upstream changes into your fork as the codebase
is in active development.

You can follow installation instructions on the [Open-eObs Readme](https://github.com/NeovaHealth/openeobs/blob/master/README.md)

## Quality measures
Before opening a pull request it's recommended that you enable [Travis CI](https://travis-ci.org) and [Codacy](https://www.codacy.com)
on your fork. 

This allows you to iron out any code style issues and ensure that your code
changes haven't impacted any other part of the code base before opening a pull
request. 

The development team cannot merge any code that fails these quality measures 
(we've literally disabled merging until everything passes).

### Travis CI
[Travis CI](https://travis-ci.org) is used to check the linting and tests after you've pushed code to 
Github.

To enable Travis CI for your fork you need to sign in with your Github 
account and enable the repository in Travis. 

### Codacy
[Codacy](https://www.codacy.com) is used to check the codebase for linting issues and increases in 
complexity and duplication within the codebase. 

To enable Codacy for your fork you need to sign in with your Github account and
enable the repository.

This will analyse the master branch by default so it's recommended you add your
development branch to the list of branches to analyse.

### Running things locally
We use the [OCA's `maintainer-quality-tools`](https://github.com/OCA/maintainer-quality-tools) configurations when linting our code,
it's recommended that you clone this repo to ensure you use the same profiles that
we use.

You can the Travis checks locally by using the following commands:
- Unit Tests - `python odoo.py -i [NAME OF MODULE TO TEST] --test-enable --stop-after-init`
- Flake8 Linting - `flake8 --config=[PATH_TO_MAINTAINER_TOOLS]/travis/cfg/travis_run_flake8.cfg openeobs`
- PyLint Linting - `pylint --load-plugins=pylint_odoo --rcfile=[PATH_TO_MAINTAINER_TOOLS]/travis/cfg/travis_run_pylint.cfg openeobs`

## Accepting a pull request
On submitting your pull request the development team will check to see if the 
Travis and Codacy integrations are passing. 

Once these checks are passed we will then review the code. When we are reviewing
code we are looking at:
- User need and if the submitted code implements new functionality how that need is met
- Design decisions such as:
  - If user configurable data is hardcoded or non-overridable
  - If the code is cohesive or could be broken into different modules
  - If the functionality is more applicable to the lower level `NHClinical` repository
  - Naming conventions (i.e. do variables names make sense)

If we have any changes we will set the pull request to the `Request Changes` state
and explain which changes we'd like. 

Upon resolving any issues we will then perform an internal manual test of the 
new functionality and on these tests passing, merge the changes into the codebase.

# Feedback, Bugs and Suggestions
If you have any feedback, bugs or suggestions about the Open-eObs project you
can open an issue.

In order to make it easier to communicate we have a set template for our issues.

For bugs it's important that you fill out the sections of this template so we 
can understand the context around the bug happening as this allows us to diagnose
the cause quickly.
