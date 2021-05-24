import scrapy
from scrapy import Request
import re

class CraigslistSpider(scrapy.Spider):
    name = 'craigslist'
    allowed_domains = ['seattle.craigslist.org']
    start_urls = ['http://seattle.craigslist.org/search/est/cta']

    def parse(self, response):
        ads = response.xpath('//div[@class="result-info"]') 
        for ad in ads: 
            title = ad.xpath('h3/a[@class="result-title hdrlnk"]/text()').extract_first() #get titles of the ad
            price = ad.xpath('span/span[@class="result-price"]/text()').extract_first() #get price of the ad
            rel_url = ad.xpath('h3/a/@href').extract_first() #get end url of the ad
            abs_url = response.urljoin(rel_url) #join the relative url with the complete url (http://..)
            if ad.xpath('span/span[@class="result-hood"]'): #to check if the neighborhood is null
                neighbor = ad.xpath('span/span[@class="result-hood"]/text()').extract_first()[2:-1]
            else:
                neighbor = "Null"
            yield Request(abs_url,callback=self.parse_page, dont_filter=True, 
                          meta={'Title': title, 'Price': price,'URL':abs_url,'Neighborhood':neighbor}) #calling function to parse the description page of the ad
            
        rel_next_url=response.xpath('//span/a[@class="button next"]/@href').extract_first()
        abs_next_url=response.urljoin(rel_next_url) 
        
        yield Request(abs_next_url,callback=self.parse) #to function the ads on the next page
        
    def parse_page(self,response):
        title = response.meta['Title'] 
        price = response.meta['Price']
        abs_url = response.meta['URL'] 
        neighbor = response.meta['Neighborhood']
        desc = "".join(response.xpath('//section[@id="postingbody"]/text()').extract()) #get the description of the ad from it's page
        final=""
        for template in desc:
            if template.isalnum() or template==" ":
                final+=template
       
        yield {'Title': title, 'Price': price,'Neighborhood':neighbor,'URL':abs_url,'Description':final}
        
        
        

