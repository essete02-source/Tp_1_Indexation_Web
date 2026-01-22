# TP_ENSAI

## TP1

### Usage

```bash
python tp1_code.py
```

## TP2 – Inverted Indexes

### Description
This project builds inverted indexes from e-commerce product data.  
These indexes are used to prepare a search engine.

### Requirements
```bash
pip install pandas nltk
```

### Usage

```bash
python tp2_code.py
```

The script reads `products.jsonl` and creates all indexes in the `indexes/` directory.

### Output Files

* `title_index.json` - Positional inverted index for product titles
* `description_index.json` - Positional inverted index for product descriptions
* `brand_index.json` - Maps product brands to URLs
* `origin_index.json` - Maps product origin countries to URLs
* `reviews_index.json` - Stores review statistics for each product

### Index Structures

#### Positional Indexes (title, description)

```json
{
  "token": {
    "url": [0, 3, 7]
  }
}
```

Each token is linked to product URLs and its positions in the text.

#### Feature Indexes (brand, origin)

```json
{
  "Apple": ["url1", "url2"],
  "Samsung": ["url3"]
}
```

Each feature value is linked to the corresponding product URLs.

#### Reviews Index

```json
{
  "url": {
    "nb_total_reviews": 15,
    "note_moyenne": 4.5,
    "derniere_note": 5
  }
}
```

This index stores review information for ranking.

### Technical Choices

* Tokenization by whitespace
* Lowercase normalization
* Punctuation removed
* English stopwords removed using NLTK
* Positions stored as integer lists

### Input Format

The input file is a JSONL file. Each line represents one product and contains:

* `url`
* `title`
* `description`
* `product_features`
* `product_reviews`

## TP3 – Search Engine

### Description
This project implements a simple search engine over the indexed product data.
It combines filtering and ranking techniques to return relevant products.

### Requirements
```bash
pip install nltk
```

## Usage
```bash
python tp3_code.py
```

The script:
* Runs a few automatic test queries
* Then starts an interactive search mode

## Features
* Token-based document filtering
* BM25 ranking on titles and descriptions
* Exact match bonus using positional indexes
* Review-based signals (average rating, number of reviews)
* Query expansion with synonyms
* Results can be exported to JSON

## Output
Search results can be saved as JSON files:
```
results_<query>.json
```

## Notes
Some products may share the same title but have different URLs. This is due to product variants or closely related products, which are represented as distinct URLs in the dataset.