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

Make sure the tests, linting and type checks are passing:

```bash
$ ./test.sh
```

Bump the version number with `poetry version`, in accordance with [semver](https://python-poetry.org/docs/cli/#version). The `version` command in `poetry` updates `poetry.toml`
  - For a bug fix / patch release, run `poetry version patch`.
  - For a new feature release, run `poetry version minor`.
  - For a breaking API change, run `poetry version major.`

Build the project: `$ ./test.sh`

```bash
$ poetry build
```

### Update the GitHub remote

Tag the release:

```bash
$ git tag -a v0.1.0 -m "my version 0.1.0"
```

Push the release:
```bash
$ git push origin --tags
```

### Publish to PyPI

Publish to [PyPI](https://pypi.org/):

```bash
$ poetry publish
```

Alternatively, configure the test site, [TestPyPI](https://test.pypi.org/):

```bash
$ poetry config repositories.test-pypi https://test.pypi.org/legacy/
$ poetry publish --repository test-pypi
```

To install from TestPyPI:

```bash
$ pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple testncbi
```
