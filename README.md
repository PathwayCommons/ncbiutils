# pubmedfetch

Making retrieval of article records from PubMed easy.

## Installation

```bash
$ pip install pubmedfetch
```

## Usage

`pubmedfetch` can be used to as follows:

```python
from pubmedfetch.pubmedfetch import get

file_path = "test.txt"  # path to your file
get(file_path)
...
```

## Contributing

Interested in contributing? Check out the contributing guidelines.
Please note that this project is released with a Code of Conduct.
By contributing to this project, you agree to abide by its terms.

## License

`pubmedfetch` was developed by Jeffrey Wong. It is licensed under the terms of the MIT license.

## Credits

`pubmedfetch` was created with [`poetry`](https://python-poetry.org/). It leans heavily on [Bio](https://biopython.org/docs/1.75/api/Bio.html).