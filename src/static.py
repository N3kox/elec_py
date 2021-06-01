# -*- coding : utf-8 -*-

dir = "/Users/mac/Desktop/毕设/数据/"
pklDir = dir + 'ws4mission/pickles/'
stopDir = dir + 'ws4mission/stopwords/'
stopFileDir = stopDir + 'baidu_stopwords.txt'
jsonDir = dir + 'ws4mission/json/'
head = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
directSearchDir = 'https://baike.baidu.com/item/'
mumbleSearchDir = 'https://baike.baidu.com/search/none?word=[wordFiller]&pn=0&rn=10&enc=utf8'
addr = ('localhost', '7687')
auth = ('neo4j', 'shuffleralt1999')