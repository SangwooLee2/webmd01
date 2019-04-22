# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WebmdItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    drugname = scrapy.Field()
    screenname = scrapy.Field()
    condition = scrapy.Field()
    comment = scrapy.Field()
    reviewer = scrapy.Field()
    effectiveness = scrapy.Field()
    easeofuse = scrapy.Field()
    satisfaction = scrapy.Field()
    NoUsefulFound = scrapy.Field()
    whois = scrapy.Field()
    gender = scrapy.Field()
    age = scrapy.Field() 
    TimeOnMed = scrapy.Field()
