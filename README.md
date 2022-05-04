# ncbiutils

![build](https://github.com/jvwong/ncbiutils/actions/workflows/build.yml/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/jvwong/ncbiutils/LICENSE)
[![codecov](https://codecov.io/gh/jvwong/ncbiutils/branch/development/graph/badge.svg?token=CANP9DIS00)](https://codecov.io/gh/jvwong/ncbiutils)

Making retrieval of records from [National Center for Biotechnology Information (NCBI)](https://www.ncbi.nlm.nih.gov/) [E-Utilities](https://www.ncbi.nlm.nih.gov/books/NBK25499/) simpler.

## Installation

Set up a virtual environment. Here, we use [miniconda](https://docs.conda.io/en/latest/miniconda.html) to create an environment named `testenv`:

```bash
$ conda create --name testenv python=3.8
$ conda activate testenv
```

Then install the package in the `testenv` environment:

```bash
$ pip install ncbiutils
```

## Usage

The `ncbiutils` module exposes a `PubMedFetch` class that provides an easy to configure and use wrapper for the [EFetch](https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch) E-Utility. By default, `PubMedFetch` will retrieve PubMed article records, each indicated by its PubMed identifier (PMID).

```python
from ncbiutils.ncbiutils import PubMedFetch

# Initalize a list of PubMed identifiers for those records we wish to retrieve
uids = ['16186693', '29083299']

# Create an instance, optionally provide an E-Utility API key
pubmed_fetch = PubMedFetch()

# Retrieve the records
# Returns a generator that yields results for a chunk of the input PMIDs (see Options)
chunks = pubmed_fetch.get_records_chunks(uids)

# Iterate over the results
for chunk in chunks:
    # Each chunk consists of a 3-tuple:
    #   - error: Includes network errors as well as HTTP status >=400
    #   - citations: article records, each wrapped as a Citation
    #   - ids: input ids for chunk
    error, citations, ids = chunk

    # Citation class can be represented as a dict
    print(citations[0].dict())
```

### Options
Configure the `PubMedFetch` instance through its constructor:

- retmax : int
  - Maximum number of records to return in a chunk (default/max 10000)
- api_key : str
  - API key for NCBI E-Utilities


## Testing

As this project was built with [poetry](https://python-poetry.org), you'll need to [install poetry](https://python-poetry.org/docs/#installation) to get this project's development dependencies.

Once installed, clone this GitHub remote:

```bash
$ git clone https://github.com/jvwong/ncbiutils
$ cd ncbiutils
```

Install the project:

```bash
$ poetry install
```

Run the test script:

```bash
$ ./test.sh
```

Under the hood, the tests are run with [pytest](https://docs.pytest.org/). The test script also does a lint check with [flake8](https://flake8.pycqa.org/) and type check with [mypy](http://mypy-lang.org/).


## Publishing a release

As this project was built with [poetry](https://python-poetry.org), you'll need to [install poetry](https://python-poetry.org/docs/#installation) first.

### Test

Make sure the tests, linting and type checks are passing:

```bash
$ ./test.sh
```

### Version

We'll use [Python Semantic Release (PSR)](https://python-semantic-release.readthedocs.io/en/latest/) to manage versioning. By making a commit with a well-defined message structure, PSR will scan commit messages and bump the version accordingly in accordance with [semver](https://python-poetry.org/docs/cli/#version).

For a patch bump:

```bash
$ git commit -m "fix(ncbiutils): some comment for this patch version"
```

For a minor bump:

```bash
$ git commit -m "feat(ncbiutils): some comment for this minor version bump"
```

For a release:

```bash
$ git commit -m "feat(mod_plotting): some comment for this release\n\nBREAKING CHANGE: other footer text."
```

Use PSR to scan commits and update the version accordingly:

```bash
$ semantic-release version -v DEBUG
```

This step automatically updated our package’s version in the pyproject.toml file and created a new tag for our package, which you could view by typing `git tag --list` at the command line.

```
$ git push --tags
```

### Publish to PyPI

Build the project:

```bash
$ poetry build
```

Optionally, test on [TestPyPI](https://test.pypi.org/):

```bash
$ poetry config repositories.test-pypi https://test.pypi.org/legacy/
$ poetry publish --repository test-pypi
```

To install from TestPyPI:

```bash
$ pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple testncbi
```

Publish to [PyPI](https://pypi.org/):

```bash
$ poetry publish
```

