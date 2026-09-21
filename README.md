# LemmeRecommend

An LLM-powered shopping assistant for people who need a product but don't know what to look for. Give it a product ("chair") and a need ("for wfh"), and it works out which specs matter, searches Amazon, and (in progress) picks the top 3 products with a plain-language explanation of why each one fits, plus a link to buy.

Built on [SerpApi](https://serpapi.com/) for Amazon data and a local LLM (via [Ollama](https://ollama.com/)) for the reasoning.

## How it works

```
 product + user requirement
            │
            ▼
 ┌─────────────────────────┐
 │ 1. Feature extraction   │  LLM (Ollama, qwen3.5:9b)
 │    features + query     │  → ordered feature list + Amazon search query
 └───────────┬─────────────┘
            ▼
 ┌─────────────────────────┐
 │ 2. Amazon search        │  SerpApi `amazon` engine
 │    up to 15 results     │  → saved to results/<product>_amazon_search_results.json
 └───────────┬─────────────┘
            ▼
 ┌─────────────────────────┐
 │ 3. Rerank  (planned)    │  score results against features + user requirement
 │    keep top 3           │
 └───────────┬─────────────┘
            ▼
 ┌─────────────────────────┐
 │ 4. Deep dive (planned)  │  SerpApi `amazon_product` engine, one call per ASIN
 │    review summary       │  → LLM writes a summary of why each product is worth buying
 └───────────┬─────────────┘
            ▼
   3 recommendations + Amazon links
```

### Status

| Step | Status |
|------|--------|
| 1. Feature extraction and search query generation | Done |
| 2. Amazon search via SerpApi, results saved as JSON | Done |
| 3. Rerank results, keep top 3 | Planned |
| 4. Fetch product details and reviews, generate summaries | Planned |
| 5. Final output: top 3 with summaries and links | Planned |

## Project layout

| File | Purpose |
|------|---------|
| `main.py` | Entry point. Extracts features and a search query, then runs the Amazon search for each row of `initial_results.csv`. |
| `prompts.py` | Prompt that asks the LLM for features and a search query as JSON. |
| `models.py` | Pydantic `Response` schema (`features`, `search_query`) used to parse the LLM output. |
| `ollama_call.py` | Thin wrapper around the Ollama chat API (`qwen3.5:9b`, thinking disabled). |
| `search_product.py` | SerpApi Amazon search. Returns the first 15 results from `amazon.in`. |
| `initial_results.csv` | Step 1 output: `Product, User Requirement, Features(AI), Search Query(AI)`. |
| `results/` | Step 2 output: one JSON file per product. |

## Setup

**Prerequisites**

- Python 3.10+
- [Ollama](https://ollama.com/) running locally with the model pulled:
  ```bash
  ollama pull qwen3.5:9b
  ```
- A [SerpApi](https://serpapi.com/) API key

**Install**

```bash
pip install ollama serpapi python-dotenv pandas pydantic langchain-core
```

**Configure**

Create a `.env` file in the project root:

```
SERP_API=your_serpapi_key
```

## Usage

`main.py` currently runs in two stages, and the feature-extraction stage is commented out. To go from scratch, uncomment the block at the top of `__main__` (it writes `initial_results.csv`), edit `product_tuples`, and run:

```bash
python main.py
```

With `initial_results.csv` already in place, `main.py` skips extraction and runs the Amazon search for every row, writing `results/<product>_amazon_search_results.json`.

### Example

Input: `("chair", "for wfh")`

Step 1 output:

```
Features:     Ergonomic lumbar support, Mesh back for breathability,
              Seat depth adjustability, Weight capacity up to 300 lbs,
              Adjustable seat height range
Search query: ergonomic mesh office chair adjustable armrests
```

Step 2 output: `results/chair_amazon_search_results.json`, a list of results with fields including `asin`, `title`, `price`, `rating`, `reviews`, `link_clean` and `bought_last_month`.

## Roadmap

### 3. Rerank to top 3

Rank the search results against the extracted features and the user requirement, and keep the best 3. The input for each result is mostly its `title` plus metadata (`price`, `rating`, `reviews`, `bought_last_month`), so the reranker needs to handle short, keyword-heavy titles.

Options to evaluate:

- **Cross-encoder reranker** (e.g. a BGE reranker): fast and cheap, scores `(requirement + features, title)` pairs.
- **LLM-as-reranker**: reuse the local Qwen model to score each result against the features. Slower, but can reason about constraints such as "supports 300 lbs".
- **Hybrid**: cross-encoder to shortlist, LLM to make the final top-3 call. Blend relevance with a quality signal (rating and review count) so that a 5-star product with 2 reviews doesn't win.

### 4. Review deep dive and summaries

For each of the top 3 products, call the SerpApi `amazon_product` engine with the product's `asin` to get details and reviews. Then have the LLM write a summary covering:

- Why this product fits the user's requirement, mapped to the extracted features
- What reviewers praise and complain about
- Trade-offs and who it is *not* a good fit for

Output per product: title, price, rating, summary, and the Amazon link.

## Known issues

- **Sponsored results are included.** SerpApi's `organic_results` for Amazon still contains sponsored listings, flagged with `"sponsored": true`. In the current saved results that is 10 of 15 for chairs, 5 of 15 for mattresses and 2 of 3 for tablets. To get true organic results, filter them out in `search_product.py` before slicing to 15. This should be done before reranking.
- **Sponsored links are click-tracking URLs.** For sponsored items, `link` is an `amazon.in/sspa/click?...` redirect. Prefer `link_clean` or build `https://www.amazon.in/dp/<asin>` for the final recommendation.
- **Failed parses are silent.** `get_product_specifications` in `main.py` catches all exceptions and returns `("None", "None")`, which would then be sent to SerpApi as a search query.
- **Search query quality varies.** The mattress query (`firm orthopedic mattress medium soft memory foam back pain relief`) contradicts itself ("firm" and "medium soft"), and the tablet query returned only 3 results.
- **Amazon India only.** `amazon_domain` is hardcoded to `amazon.in`.

## License

See [LICENSE](LICENSE).
