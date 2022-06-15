# ncbiutils

![build](https://github.com/PathwayCommons/ncbiutils/actions/workflows/build.yml/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/PathwayCommons/ncbiutils/LICENSE)
[![codecov](https://codecov.io/gh/PathwayCommons/ncbiutils/branch/main/graph/badge.svg?token=CFD1jGfNKl)](https://codecov.io/gh/PathwayCommons/ncbiutils)
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
import json

# Initalize a list of PubMed identifiers for those records we wish to retrieve
uids = ['16186693', '29083299']

# Create an instance, optionally provide an E-Utility API key
pubmed_fetch = PubMedFetch()

# Retrieve the records
# Returns a generator that yields results for a chunk of the input PMIDs (see Options)
chunks = pubmed_fetch.get_citations(uids)

# Iterate over the results
for chunk in chunks:
    # A Chunk is a namedtuple with 3 fields:
    #   - error: Includes network errors as well as HTTP status >=400
    #   - citations: article records, each wrapped as a Citation
    #   - ids: input ids for chunk
    error, citations, ids = chunk

    # Citation class can be represented as a dict
    print(json.dumps(citations[0].dict()))

# Output as JSON
{
   "pmid":"16186693",
   "pmc":"None",
   "doi":"10.1159/000087186",
   "title":"Searching the MEDLINE literature database through PubMed: a short guide.",
   "abstract":"The Medline database from the National Library of Medicine (NLM) contains more than 12 million bibliographic citations from over 4,600 international biomedical journals...",
   "author_list":[
      {
         "fore_name":"Edith",
         "last_name":"Motschall",
         "initials":"E",
         "collective_name":"None",
         "orcid":"None",
         "affiliations":[
            "Institut für Medizinische Biometrie und Medizinische Informatik, Universität Freiburg, Germany. motschall@mi.ukl.uni-freiburg.de"
         ],
         "emails":[
            "motschall@..."
         ]
      },
      ...
   ],
   "journal":{
      "title":"Onkologie",
      "issn":[
         "0378-584X"
      ],
      "volume":"28",
      "issue":"10",
      "pub_year":"2005",
      "pub_month":"Oct",
      "pub_day":"None"
   },
   "publication_type_list":[
      "D016428",
      "D016454"
   ],
   "correspondence":[],
   "mesh_list":[
      {
         "descriptor_name":{
            "ui":"D003628",
            "value":"Database Management Systems"
         }
      },
      {
         "descriptor_name":{
            "ui":"D016206",
            "value":"Databases, Bibliographic"
         }
      },
      {
         "descriptor_name":{
            "ui":"D016247",
            "value":"Information Storage and Retrieval"
         },
         "qualifier_name":[
            {
               "ui":"Q000379",
               "value":"methods"
            }
         ]
      },
     ...
   ]
}
```

*Options*

Configure the `PubMedFetch` instance through its constructor:

- db: DbEnum
  - Set the database to process either `<!DOCTYPE pmc-articleset ...>` or `<!DOCTYPE PubmedArticleSet ...>` (default)
- retmax : int
  - Maximum number of records to return in a chunk (default/max 10000)
- api_key : str
  - API key for NCBI E-Utilities

---

Also available is:
  - `PubMedDownload` that can retrieve records from the PubMed FTP server for both [baseline and daily updates](https://pubmed.ncbi.nlm.nih.gov/download/).

## Testing

As this project was built with [poetry](https://python-poetry.org), you'll need to [install poetry](https://python-poetry.org/docs/#installation) to get this project's development dependencies.

Once installed, clone this GitHub remote:

```bash
$ git clone https://github.com/PathwayCommons/ncbiutils
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

A GitHub workflow will automatically version and release this package to [PyPI](https://pypi.org/) following a push directly to `main` or when a pull request is merged into `main`. A push/merge to `main` will automatically bump up the patch version.

We use [Python Semantic Release (PSR)](https://python-semantic-release.readthedocs.io/en/latest/) to manage versioning. By making a commit with a well-defined message structure, PSR will scan commit messages and bump the version accordingly in accordance with [semver](https://python-poetry.org/docs/cli/#version).

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
