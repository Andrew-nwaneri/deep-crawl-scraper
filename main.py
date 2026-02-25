import scrapy
from scrapy.crawler import CrawlerProcess

class QuotesSpider(scrapy.Spider):
    name = 'quotes_spider'
    start_urls = ['https://quotes.toscrape.com/']

    def parse(self, response):
        for quote in response.css('div.quote'):
            item = {
                'quote_text': quote.css('span.text::text').get(),
                'author_name': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

            author_url = quote.css('span a::attr(href)').get()
            if author_url:
                # --- THE FIX IS HERE ---
                # Adding dont_filter=True tells Scrapy to visit the author page
                # even if it has already visited it for a previous quote.
                yield response.follow(
                    author_url,
                    self.parse_author,
                    meta={'item': item},
                    dont_filter=True
                )

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_author(self, response):
        item = response.meta['item']
        item['author_full_name'] = response.css('h3.author-title::text').get(default='').strip()
        item['date_of_birth'] = response.css('span.author-born-date::text').get()
        item['place_of_birth'] = response.css('span.author-born-location::text').get(default='').replace('in ', '').strip()
        yield item

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'FEED_URI': 'quotes_data.json',
        'LOG_LEVEL': 'INFO',
        'FEED_EXPORT_ENCODING': 'utf-8'
    })

    process.crawl(QuotesSpider)
    process.start()