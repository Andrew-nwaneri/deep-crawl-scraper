import scrapy
from scrapy.crawler import CrawlerProcess


class QuotesSpider(scrapy.Spider):
    name = 'quotes_spider'
    start_urls = ['https://quotes.toscrape.com/']

    def parse(self, response):
        """
        Main parser for the quote listings and pagination.
        """
        # 1. Loop through each quote container on the page
        for quote in response.css('div.quote'):
            # Basic data from the main page
            item = {
                'quote_text': quote.css('span.text::text').get(),
                'author_name': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

            # 2. Find the link to the Author Profile
            author_url = quote.css('span a::attr(href)').get()

            # 3. "Yield" a request to the author page, passing our current data in 'meta'
            # This allows us to combine main page data with bio page data later
            yield response.follow(author_url, self.parse_author, meta={'item': item})

        # 4. Handle Pagination: Find the 'Next' button
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_author(self, response):
        """
        Parser for the individual author profile pages.
        """
        # Retrieve the item we started building in the parse method
        item = response.meta['item']

        # Extract the deep-dive bio data
        item['author_full_name'] = response.css('h3.author-title::text').get().strip()
        item['date_of_birth'] = response.css('span.author-born-date::text').get()
        item['place_of_birth'] = response.css('span.author-born-location::text').get().replace('in ', '')

        yield item


# --- Execution Logic ---
if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',  # Save results as JSON
        'FEED_URI': 'quotes_data.json',  # Filename
        'LOG_LEVEL': 'INFO',  # Clean up the console output
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    process.crawl(QuotesSpider)
    process.start()
    print("\nScraping complete! Check 'quotes_data.json' for the results.")