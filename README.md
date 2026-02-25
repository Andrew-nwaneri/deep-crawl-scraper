[README.md](https://github.com/user-attachments/files/25541783/README.md)
# deep-crawl-scraper
This is an assessment project to evaluate my understanding and practical approach to scraping data and handling technical decision making

This project is a high-performance web scraper designed to extract quotes, their associated tags, and detailed author biographies from [Quotes to Scrape](https://quotes.toscrape.com/).

## 1. Overall Approach

To meet the requirements of deep navigation and efficiency, I chose **Scrapy** as the core framework.

Unlike simple parsing libraries, Scrapy allows for an **asynchronous architecture**. This means the spider doesn't wait for one page to finish loading before starting the next. It treats every quote as a "trigger" to start a secondary request for the author’s biography, merging the data in flight.

---

## 2. Pagination and Navigation

The scraper uses a recursive "follow" logic to ensure no data is left behind:

* **Vertical Navigation:** The spider identifies the "Next" button at the bottom of the page using CSS selectors (`li.next a::attr(href)`). If the link exists, the spider yields a new request to itself, effectively looping through all 10 pages.
* **Horizontal (Deep) Navigation:** For every quote found on a listing page, the spider extracts the relative URL for the author’s bio. It then uses `response.follow` to jump into the profile page.
* **Data Passing:** I utilized the `meta` attribute in Scrapy’s request objects to "carry" the quote text and tags into the author-parsing function, ensuring the bio data is attached to the correct quote.

---

## 3. Challenges & Solutions

| Challenge | Impact | Solution |
| --- | --- | --- |
| **The 50-Item Limit** | Scrapy’s Duplicate Filter was skipping authors who had already been visited, resulting in only ~50 results instead of 100. | Implemented `dont_filter=True` in the author request to ensure every quote triggers a bio-merge, regardless of repeat authors. |
| **Unicode Escaping** | Output files contained sequences like `\u00e9` instead of accented characters like `é`. | Configured `'FEED_EXPORT_ENCODING': 'utf-8'` in the crawler settings to force human-readable text. |

---

## 4. Future Improvement: Robustness & Scaling

If given more time, the primary improvement I would implement is **Proxy Rotation and User-Agent Randomization**.

While this specific site is designed for practicing scraping, most real-world targets use sophisticated anti-bot measures. I would integrate a middleware (like `scrapy-user-agents`) to rotate the browser identity for every request. Additionally, I would implement an **Item Pipeline** to clean the data (e.g., converting "Date of Birth" strings into actual Python `datetime` objects) before saving them to a structured SQL database like PostgreSQL.

---
