from scrapy import Spider
from webMD.items import WebmdItem
import re
from scrapy import Request

age_set = ['0-2', '3-6', '7-12', '13-18','19-24', '25-34','35-44', '45-54', '55-64', '65-74', '75 or over' ]
gender_set=['Male', 'Female']
whois_set = ['Patient', 'Caregiver']
TimeOnMed_set=['less than 1 month', '1 to 6 months', '6 months to less than 1 year', \
                  '1 to less than 2 years','2 to less than 5 years', \
                  '5 to less than 10 years', '10 years or more']


class WebMDSpider(Spider):
    name = "webmd_spider"
    allowed_urls = ['https://www.webmd.com/']
    start_urls = ['https://www.webmd.com/drugs/2/condition-1432/hypertension']
    
    
    def parse(self, response): 
        # teacher: make sure this one works first
        # 4/18 lsw blocked, rows = response.xpath('//*[@id="ContentPane30"]/div/table/tbody/tr') # all drugs for one symptom 
        
        rows = response.xpath('//*[@id="ContentPane30"]/div/table/tbody/tr/td/a/@href').extract()    
            # returned in trhe order of detail => review page => detail => review page... along the row direcgtion 
            # start with '/'. Avvoid redundancy when joising with webmd www site. 
        rows = [rows[ii] for ii in range(1,len(rows),2)]
        
        # rows = rows[10] # further downselection 
        rows = rows[0:10] # further downselection 

     
        for row_i in range(0, len(rows)):
            row = rows[row_i]    
            # one medication # 
            # drugname = row.xpath('./td[1]/a/text()').extract()[0] # string     
            # NoReviews = int( row.xpath('./td[4]/a/text()').extract()[0].split()[0]  ) # integer 
            
            # method 1
            # UserReviewUrl = 'https://www.webmd.com/drugs/drugreview-6873-lisinopril.aspx?drugid=6873&drugname='+drugname
                
            # method 2 
            temp = [ '//*[@id="ContentPane30"]/div/table/tbody/tr[{}]/td[4]/a/@href'.format(row_i+1) ]
            url_part_temp = response.xpath(temp[0]).extract()[0]
            # => this returns:    '/drugs/drugreview-6873-lisinopril.aspx?drugid=6873&drugname=lisinopril, for example    
            reviewpage_url =  'https://www.webmd.com/' + url_part_temp[1:]  
            # example) https://www.webmd.com/drugs/drugreview-6873-lisinopril.aspx?drugid=6873&drugname=lisinopril
        
            yield Request(url=reviewpage_url, callback=self.parse_review_page) # review page for a specific drug 
   
    

    def parse_review_page(self, response): # for a specific drug
        
        print('*************************** **********************')
        
        text = response.xpath('//*[@id="ratings_fmt"]/div[3]/div[2]/text()').extract_first()
        text2 = list( map(lambda x: int(x), re.findall('\d+', text )) ) # three numbers as a list
        per_page = text2[1]+1-text2[0]
        NtotalRev = text2[2] # actualy needs to be corrected at this moment    
        
        number_pages = NtotalRev // per_page
        
        temp = response.xpath('//*[@id="UserRater"]/script/text()').extract() # url part for this page
        temp = temp[0].split()
        temp2 = temp[3][2:-2]  # returns 'drugs/drugreview-6873-lisinopril+oral.aspx?drugid=6873&drugname=lisinopril+oral&appId=1&conditionFilter='
        revPageUrl_start = 'https://www.webmd.com/' + temp2 +'-500' + '&sortby=3&pageIndex={}'
        revPageUrls = [revPageUrl_start.format(x) for x in range(0,number_pages)]
        

        for url in revPageUrls:
            yield Request(url=url, callback=self.parse_revdetail_page) 
            # call per page, each page showing 5 review opinions

    def parse_revdetail_page(self, response):
          
        text = response.xpath('//*[@id="ratings_fmt"]/div[3]/div[2]/text()').extract_first()
        text2 = list( map(lambda x: int(x), re.findall('\d+', text )) ) # three numbers as a list
        per_page = text2[1]+1-text2[0]       
        
        
   
        for rev_i in range(0, per_page):
            temp = response.xpath( '//*[@id="ratings_fmt"]/div[{x}]/div[1]/div[1]/text()'.format(x=rev_i+4) ).extract()  # div[4] [5]....
            temp = re.split('[\r\n\t:]+',temp[0] )
            condition = temp[2][1:] # a string
            
            drugname = temp = response.xpath('//*[@id="header"]/div/h1/text()').extract()
            drugname = drugname[0].replace("User Reviews & Ratings - ", "") # so that obly drug name is left
            
        
            ###############################
            #comment = response.xpath( '//*[@id="comTrunc{x}"]/text()'.format(x=rev_i+1) ).extract() # a strnbg # comTruc1,2,3....
            comment = response.xpath( '//*[@id="comFull{x}"]/text()'.format(x=rev_i+1) ).extract() # a strnbg # comTruc1,2,3....
            # note) //*[@id="comTrunc1"]/text()  vs.   //*[@id="comFull1"]/text()
    
            
            if( len(comment)>0 ): # otherwise, error is encountered
                comment = comment[0]
   
            reviewer = response.xpath( '//*[@id="ratings_fmt"]/div[{x}]/p[1]/text()'.format(x=rev_i+4)  ).extract()[0] # a string  # div[4] [5].....
            
            effectiveness = response.xpath('//*[@id="ctnStars"]/div[1]/p[2]/span/text()').extract()[rev_i+1] # [1] for rev_i 1, [2] for rev_i 2
            effectiveness = int( effectiveness[-1] )
        
            easeofuse = response.xpath('//*[@id="ctnStars"]/div[2]/p[2]/span/text()').extract()[rev_i+1]  # [1] for rev_i 1, [2] for rev_i 2
            easeofuse = int( easeofuse[-1] )
     
            satisfaction = response.xpath('//*[@id="ctnStars"]/div[3]/p[2]/span/text()').extract()[rev_i+1]  # [1] for rev_i 1, [2] for rev_i 2
            satisfaction = int( satisfaction[-1])
            
            NoUsefulFound = response.xpath('//*[@id="ratings_fmt"]/div[{x}]/div[3]/p/text()[1]'.format(x=rev_i+4)).extract() # string in []
            
            if len(NoUsefulFound)>0: # ['   ']
                if len( re.findall( '[0-9]+', NoUsefulFound[0] ) )> 0:    # '   '
                    NoUsefulFound = int( re.findall( '[0-9]+', NoUsefulFound[0] )[0] )
                else:
                    NoUsefulFound = 0
            else:
                NoUsefulFound = 0
                    
            
            # 'reviewer' further analysis         
            whois = [x for x in whois_set if reviewer.find(x)>=0]
            if len(whois)>0:
                whois = whois[0]
                reviewer=reviewer.replace(whois,'')
            else:
                whois = None
                
            gender = [x for x in gender_set if reviewer.find(x)>=0]
            if len(gender)>0:
                gender = gender[0]
                reviewer=reviewer.replace(gender,'')   
            else:
                gender=None
            
            age = [x for x in age_set if reviewer.find(x)>=0]
            if len(age)>0:
                age = age[0]
                reviewer=reviewer.replace(age,'')
            else: 
                age=None
                
            TimeOnMed = [x for x in TimeOnMed_set if reviewer.find(x)>=0]
            if len(TimeOnMed)>0:
                TimeOnMed = TimeOnMed[0]
                reviewer=reviewer.replace(TimeOnMed,'')
            else:
                TimeOnMed=None
                
            reviewer = reviewer.replace('Reviewer: ','')    
            reviewer = reviewer.replace('on Treatment for','')
            reviewer = reviewer.replace('()','')
            if( len(re.findall('[a-zA-Z0-9]+', reviewer)) > 0):
                screenname = re.findall('[a-zA-Z0-9]+', reviewer)[0]
                reviewer = reviewer.replace(screenname,'')
            else:
                screenname =None
            

            item =  WebmdItem()
            item['drugname']=drugname
            item['screenname']=screenname
            item['condition']=condition
            item['comment']=comment
            item['reviewer']=reviewer
            item['effectiveness']=effectiveness
            item['easeofuse']=easeofuse
            item['satisfaction']=satisfaction
            item['NoUsefulFound']= NoUsefulFound
            item['whois']=whois
            item['gender']=gender
            item['age']=age
            item['TimeOnMed']=TimeOnMed
            
        
            yield item 
            
