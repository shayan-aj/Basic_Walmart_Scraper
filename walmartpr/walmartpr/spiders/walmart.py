import scrapy
from scrapy_selenium import SeleniumRequest
from urllib.parse import urlencode

API_KEY = '0e806f13-864d-479a-b8c8-eff82d186d03'

def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url


class WalmartSpider(scrapy.Spider):
    name = "walmart"
    allowed_domains = ["walmart.com", "proxy.scrapeops.io"]

    def __init__(self):
        self.counter = 1
        self.last_page = None

    def start_requests(self):
        url = 'https://www.walmart.com/search?q=iphone+16&affinityOverride=default&sort=best_match'
        yield SeleniumRequest(url=get_proxy_url(url), callback=self.parse,
        script="window.scrollTo(0, document.body.scrollHeight);")

    def parse(self, response):
        if self.last_page is None:
            labels = response.css("li.sans-serif")
            if labels and len(labels) > 1:
                last_page_text = labels[-2].css("a::text").get()
                if last_page_text and last_page_text.isdigit():
                    self.last_page = int(labels[-2].css("a::text").get())
                else: print("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")

        items = response.css("div.mb0")
        
        for item in items:
            item_url = item.css("div div a::attr(href)").get()
            if item_url:
                finished_url = "https://www.walmart.com/" + item_url
                yield SeleniumRequest(url=get_proxy_url(finished_url), callback=self.parse_item,)

        if self.last_page and self.counter < self.last_page:
            self.counter += 1
            url = f'https://www.walmart.com/search?q=iphone+16&affinityOverride=default&sort=best_match&page={self.counter}'
            yield SeleniumRequest(url=get_proxy_url(url), callback=self.parse,
            script="window.scrollTo(0, document.body.scrollHeight);")
    
    def parse_item(self, response):
        def about():
            lines = response.css("div.expand-collapse-content ul")
            lines_output = ""
            for li in lines:
                lines_output + lines.css("li::text").get() + "\n"
            return lines_output


        yield{
            "name": response.css("h1.lh-copy::text").get(),
            "rating": response.css("div.flex span.f7::text").get(),
            "price": response.css("span.inline-flex span::text").get(),
            "price per month": response.css("span.lh-copy span span::text").get(),
            "about": about()
        }

