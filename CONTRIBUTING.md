# Contributing to Mangum

Hello. Contributions to this project are highly encouraged and appreciated. This document will outline some general guidelines for how to get started.

## Contents

- [Creating a pull request](#creating-a-pull-request)
  * [Setting up the repository](#setting-up-the-repository)
- [Developing the project locally](#developing-the-project-locally)
  * [Setup](#setup)
  * [Test](#test)
    + [Coverage requirements](#coverage-requirements)
  * [Lint](#lint)
    + [Code style and formatting](#code-style-and-formatting)
    + [Static type checking](#static-type-checking)
- [Using the issue tracker](#using-the-issue-tracker)
  * [Technical support](#technical-support)
  * [Feature requests](#feature-requests)

## Creating a pull request

Non-trivial changes, especially those that could impact existing behaviour, should have an associated issue created for discussion. An issue isn't strictly required for larger changes, but it can be helpful to discuss first.

Minor changes generally should not require a new issue and can be explained in the pull request description.

### Setting up the repository

To create a pull request, you must first [fork](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-forks) the repository in GitHub, then clone the fork locally.

```shell
git clone git@github.com:<YOUR-USERNAME>/mangum.git
```

Then add the upstream remote to keep the forked repo in sync with the original.

```shell
cd mangum
git remote add upstream https://github.com/jordaneremieff/mangum.git
git fetch upstream
```

Then to keep in sync with changes in the primary repository, you pull the upstream changes into your local fork.

```shell
git pull upstream main
```

## Developing the project locally

There are a few scripts in place to assist with local development, the following scripts are located in the `/scripts` directory:

### Setup

Running the setup script will create a local Python virtual environment. It assumes that `python3.7` is available in the path and will install the development dependencies located in `requirements.txt`.

```shell
./scripts/setup
```

Alternatively, you may create a virtual environment and install the requirements manually:

```
python -m venv venv
. venv/bin/active
pip install -r requirements.txt
```

This environment is used to run the tests for Python versions 3.7, 3.8, 3.9, and 3.10.

### Test

The test script will run all the test cases with [PyTest](https://docs.pytest.org/en/stable/) using the path for the virtual environment created in the setup step (above).

```shell
./scripts/test
```

It also runs [Coverage](https://coverage.readthedocs.io/en/coverage-5.3/) to produce a code coverage report.

#### Coverage requirements

The coverage script is intended to fail under 100% test coverage, but this is not a strict requirement for contributions. Generally speaking at least one test should be included in a PR, but it is okay to use `# pragma: no cover` comments in the code to exclude specific coverage cases from the build.

### Lint

The linting script will handle running [mypy](https://github.com/python/mypy) for static type checking, and [black](https://github.com/psf/black) for code formatting.

```shell
./scripts/lint
```

#### Code style and formatting

Black formatting is required for all files with a maximum line-length of `88` (black's default) and double-quotes `"` are preferred over single-quotes `'`, otherwise there aren't specific style guidelines.

#### Static type checking

Mypy is used to handle static type checking in the build, and [type annotations](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) should be included when making changes or additions to the code. However, it is okay to use `# type: ignore` comments when it is unclear what type to use, or if the annotation required to pass the type checker significantly decreases readability.

## Using the issue tracker

The issue [tracker](https://github.com/jordaneremieff/mangum/issues) can be used for different types of discussion, but it is mainly intended for items that are relevant to this project specifically.

Here are a few things you might consider before opening a new issue:

- Is this covered in the [documentation](https://mangum.io/)?

- Is there already a related issue in the [tracker](https://github.com/jordaneremieff/mangum/issues)?

- Is this a problem related to Mangum itself or a third-party dependency?

It may still be perfectly valid to open an issue if one or more of these is true, but thinking about these questions might help reveal an existing answer sooner.

### Technical support

You may run into problems running Mangum that are related to a deployment tool (e.g. [Serverless Framework](https://www.serverless.com/)), an ASGI framework (e.g. [FastAPI](https://fastapi.tiangolo.com/)), or some other external dependency. It is okay to use the tracker to resolve these kinds of issues, but keep in mind that this project does not guaruntee support for all the features of any specific ASGI framework or external tool.

**Note**: These issues will typlically be closed, but it is fine to continue discussion on a closed issue. These issues will be re-opened only if a problem is discovered in Mangum itself.

### Feature requests

This project is intended to be small and focused on providing an adapter class for ASGI applications deployed in AWS Lambda. Feature requests related to this use-case will generally be considered, but larger features that increase the overall scope of Mangum are less likely to be included.

If you have a large feature request, please make an issue with sufficient detail and it can be discussed. Some feature requests may end up being rejected initially and re-considered later.

## Thank you

:)
