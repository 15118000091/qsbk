#encoding=utf-8
'''
Created on 2016年1月20日
添加访问头可以访问糗事百科，
解析数据，保存数据
保存最新的35页数据
下载图片 线程
保存数据到数据库

@author: haibara
'''

import urllib2
import urllib
from urllib2 import Request, HTTPError
import re
from bs4 import BeautifulSoup
import os
import logging
import time

''' 配置log信息 '''
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='qsbk.log',
                filemode='w')
# url = 'http://www.qiushibaike.com/'
class QSBK():
    #访问糗事百科需要添加head信息
    header =  {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
    }
    base_path = os.getcwd() + '\\qsbk\\'
    DEBUG = True
    base_url = 'http://www.qiushibaike.com/'
    #获取数据
    def getData(self, url):
        try :
             request = urllib2.Request(url, headers=self.header)
             response = urllib2.urlopen(request)
        except HTTPError as e:
            print(e)
            logging.error('getData error {0}'.format(e))
        data = response.read().decode('utf-8', 'replace')
        return data
    
    def singePageInfo(self,url,name):
        data = self.getData(url)
        soup = BeautifulSoup(data, "html.parser", from_encoding='utf-8')
        self.saveInfo(name, soup)
        self.downUserImages(soup)
    
    def parseQSBKTag(self,soup):
        return soup.findAll('div', {'id' : re.compile(r'qiushi_tag_\d*')})
    #解析出发表端子的所有用户名
    def parseUsers(self,soup):
        return soup.findAll('div', {'class' : 'author clearfix'})
    
    #下载用户头像图片
    def downUserImages(self,soup):
        imgs = soup.findAll('img')
        self.checkPath(self.base_path)
        for x in imgs:
            name = x['alt']
            try:
                path = self.base_path + name + '.jpg'
                if self.DEBUG:
                    print(path)
                logging.debug('save image path: {0}'.format(path))
                urllib.urlretrieve(x['src'], path)
            except Exception as e:
                logging.error('down image {0} has occur exception'.format(name))
                continue
#         return re.search(regx, data).group(2)
    
    def parseContents(self,soup):
        return soup.findAll('div', {'class' : 'content'})#根据标签属性后去数据

    #解析笑脸
    def parseVotes(self,soup):
        return soup.findAll('span', {'class' : 'stats-vote'})
    
    #解析评论数
    def parseComments(self,soup):
        return soup.findAll('a', {'class' : 'qiushi_comments'})
    
    # ascii 转换为utf-8
    def changeFormate(self,tag):
        return tag.text.strip().encode('utf-8', 'replace')
    
    #保存解析的数据到文件
    def saveInfo(self, name, soup):
        users = self.parseUsers(soup);
        contents = self.parseContents(soup)
        votes = self.parseVotes(soup)
        comments = self.parseComments(soup)
        self.checkPath(self.base_path)
        path = self.base_path + name
#         f = open(path,'w+')#会覆盖掉原先写入的
        f = open(path,'a')#追加的方式写入文件
        for item in range(len(users)) :
            if self.DEBUG :
                print('-------------------')
                print('user = ' + self.changeFormate(users[item]))
                print('content = ' + self.changeFormate(contents[item]))
                print('vote = ' + self.changeFormate(votes[item]))
                print('comments = ' + self.changeFormate(comments[item]))
                print('-------------------')
            f.write('---------- qsbk -----------' + '\n')
            f.write('user = ' + self.changeFormate(users[item])+ '\n')
            f.write('content = ' + self.changeFormate(contents[item])+ '\n')
            f.write('vote = ' + self.changeFormate(votes[item])+ '\n')
            f.write('comments = ' + self.changeFormate(comments[item])+ '\n')
#         f.flush()
        f.close()
    
    def test(self, url):
        print(self.base_path)
        if not os.path.exists(self.base_path) :
            os.makedirs(self.base_path)
            
    def checkPath(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    #获取最近8小时的内容        
    def eightHour(self):
        #http://www.qiushibaike.com/8hr/page/2/?s=4844656
        
        name = 'qsbk_8hr_' + str(int(time.time())) + '.txt'
        print(name)
        logging.debug('save info file name : {0}'.format(name))
        self.singePageInfo(self.base_url,name)#解析第一页数据
        page = 35#访问后续20页数据，一般是只有最新的35页数据
        base_8hr_url = self.base_url + '8hr/page/'
        for num in range(2, page):
            url = base_8hr_url + str(num) + '/?s=4844656'
            logging.debug('parse page url = {0}'.format(url))
            self.singePageInfo(url, name)
    
    #24小时最热的段子
    def hotInfo(self):
        name = 'qsbk_hot_' + str(int(time.time())) + '.txt'
        print(name)
        logging.debug('save info file name : {0}'.format(name))
        base_hot_url = self.base_url + 'hot'
        self.singePageInfo(base_hot_url,name)#解析第一页数据
        page = 35#访问后续20页数据，一般是只有最新的35页数据
        hot_url = base_hot_url + '/page/'
        for num in range(2, page):
            url = hot_url + str(num) + '/?s=4844662'
            logging.debug('parse page url = {0}'.format(url))
            self.singePageInfo(url, name)
    
def main():
    qsbk = QSBK()
#     qsbk.test(url)
#     qsbk.eightHour()
    qsbk.hotInfo()

if __name__ == '__main__':
  main()