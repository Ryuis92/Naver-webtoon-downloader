from html.parser import HTMLParser

class FindLatestHTMLParser(HTMLParser):
    """
    format  :   the url of the lastest episode of the webtoon
    title   :   the title of the webtoon
    """
    find_table = False
    find_detail = False
    format = None
    title = None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.find_table = True
        elif self.find_table and tag == 'a':
            if '/webtoon/detail.nhn' in attrs[0][1] and not self.format:
                self.format = 'https://comic.naver.com' + attrs[0][1]
                #print(self.format)

        elif tag == 'meta':
            if len(attrs) and attrs[0][1] == 'og:title':
                self.title = attrs[1][1] 
 

class FindDownloadListHTMLParser(HTMLParser):
    """
    url_list    :   list of urls of imgs in an episode url
    title       :   the title of an episode 
    """
    
    find_div = False
    url_list = []
    title = None

    def handle_starttag(self, tag, attrs):
        #if tag == 'div' and attrs[0][1] == 'wt_viewer':
        #    self.find_div = True
        if tag == 'div':
            if len(attrs) and attrs[0][1] == 'wt_viewer':
                self.find_div = True
        
        elif tag == 'img' and self.find_div:
            self.url_list.append(attrs[0][1])
            #print(attrs[0][1])
        
        elif tag == 'meta':
            if len(attrs) and attrs[0][1] == 'og:title':
                self.title = attrs[1][1] 
        

    def handle_endtag(self, tag):
        if self.find_div and tag == 'div':
            self.find_div = False