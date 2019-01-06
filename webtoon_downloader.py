import requests
import os
from MyHTMLParser import *
import re
import time
from multiprocessing import Process, current_process

class Webtoon_downloader():        
    
    def __init__(self):
        self.last = None                #last episode
        self.title = None               #title of webtoon
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        self.url_format = None          #e.g: https://comic.naver.com/webtoon/detail.nhn?titleId={}&no=1&weekday=mon
        self.process_num = 2
  
        
    def init(self, url):
        response = requests.get(url)
        if not response.status_code == 200:
            print("requests.get(url) failed!")
            exit(0)
        
        parser = FindLatestHTMLParser() 
        parser.feed(response.text)
        result = parser.format          #e.g: https://comic.naver.com/webtoon/detail.nhn?titleId=183559&no=1&weekday=mon

        self.title = parser.title   
        self.last = result.split('&')[1].split('=')[1]  #find lastest episode number
        self.format = result.replace(self.last, '{}')
        
    def download(self, start, end, interval):
        print("start downloading - ", current_process().name)
        error= []                                                   #connection, timeout error happens from time to time
                                                                    #error is list of dict in the form {'url' : url, 'filename': filename}

        for num in range(start, end+1, interval):
            response = requests.get(self.format.format(num))        #url of episode
            if not response.status_code == 200:
                print("Episode url error!")
                exit(0)

            parser = FindDownloadListHTMLParser()
            parser.feed(response.text)
            response.close()
            url_list = parser.url_list                              #list of img url in an episode

            count = 1                                               #for img file numbering
                                                                    #download
            for item in url_list:                                   #url of images
                try:
                    response = requests.get(item, headers = self.headers)

                    if response.status_code == 200:
                        if not os.path.isdir('.\\{0}\\{1}\\'.format(self.title, parser.title,)):
                            os.makedirs(os.path.join('.\\{0}\\{1}\\'.format(self.title, parser.title)))

                        filename = '.\\{0}\\{1}\\img{2:03}.jpg'.format(self.title, parser.title, count)
                        
                        with open(filename ,"wb") as fh:
                            fh.write(response.content)
                    response.close()        
                    count += 1              
                except:
                    print("에러발생" , parser.title, item)
                    error.append({'url' : item, 'filename':filename})
                                                                    #try urls that raised exceptions again
            for err in error:
                try:
                    response = requests.get(err['url'], headers = self.headers)
                    if response.status_code == 200:
                        with open(err['filename'] ,"wb") as fh:
                            fh.write(response.content)
                    response.close()
                    print(err["에러 해결", parser.title. err['url'])
                except: 
                    print(err['filename'], 'fail to download')

            print(parser.title, 'download complete', current_process().name)

    def main(self):
        url = input("URL of naver Webtoon: ")
        if 'https://comic.naver.com/webtoon/list.nhn?titleId=' in url:
            self.init(url)
        else:
            print(url, 'is not valid URL')
            return False
        print('initializing is done.')        
        
        while True:
            ins = input('from what episode to what episode to download? (1 ~ %s)  (int, int): ' % self.last)
            start, end = map(int,re.split('[, ]', ins))
            
            if 0 < start <= end <= int(self.last):
                break
            else:
                print('start and end is not valid.')
            
        temp = int(input("number of process (default = 2):  "))
        if temp > 0:
            self.process_num = temp
        
        print('Download episodes of {} from {} to {} with {} process'.format(self.title, start, end, self.process_num))        
        
        procs = []
        start_time = time.time()
        for i in range(self.process_num):
            if i < end:
                proc = Process(target = self.download, args=((start+i),end, self.process_num), daemon = True)
                procs.append(proc)
                proc.start()
        
        for proc in procs:
            proc.join()
        print("All Done!")
        end_time = time.time()
        print("--- %.3f seconds ---" % (end_time - start_time))
        
        return True

if __name__ == '__main__':
    down = Webtoon_downloader()
    while True:
        finish = down.main()
        if finish:
            break
