# Bookshelf

## Overview
Bookshelf is a Python package designed to fetch and generate EPUB books from online sources. It automates the retrieval and formatting of novel chapters, converting them into a structured EPUB format.

## Features
- **Web Scraping**: Retrieves novel metadata and chapters from specified URLs.
- **Data Cleaning**: Formats raw HTML into well-structured EPUB content.
- **EPUB Generation**: Creates EPUB files with proper metadata and cover images.
- **Multi-threading**: Optimized fetching of chapters using concurrent requests.

## Installation
Clone this repository and install dependencies:

```sh
    git clone https://github.com/BuzLclair/Bookshelf.git
    cd Bookshelf
    pip install requests tqdm shutil threading time
```

# Usage
## Generate EPUB:
Run the following command to generate an EPUB file:

``` sh
    python epub_generator.py
```
This script fetches novel data, processes the chapters, and outputs a formatted EPUB file.


