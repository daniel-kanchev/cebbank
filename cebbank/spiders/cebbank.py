import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from cebbank.items import Article


class cebbankSpider(scrapy.Spider):
    name = 'cebbank'
    start_urls = ['http://www.cebbank.com/site/ceb/gddt/mtgz/index.html']
    page = 1

    def parse(self, response):
        links = response.xpath('//a[@istitle="true"]/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)

            self.page += 1

            next_page = f'http://www.cebbank.com/site/ceb/gddt/mtgz/38b64d48-{self.page}.html'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="title"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="creatDate"]/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="xilan_con"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
