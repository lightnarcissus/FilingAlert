# Filing Scraper


-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

### Prerequisites
- Python >=3.7 and Pip
```console
pip install hatch
```
```console
hatch build
```
Set environment variable `S3_BUCKET_NAME` to your S3 bucket.
```console
pip install -v .
pip install -t ./dist/lambda .
```
## License

`filing-scraper` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
