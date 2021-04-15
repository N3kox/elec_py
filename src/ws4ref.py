# -*- coding: UTF-8 -*-

import requests
import re

roots = ['https://www.21ks.net/lunwen/dljslw/',
         'https://www.21ks.net/lunwen/dljslw/List_4.html',
         'https://www.21ks.net/lunwen/dljslw/List_3.html',
         'https://www.21ks.net/lunwen/dljslw/List_2.html',
         'https://www.21ks.net/lunwen/dljslw/List_1.html']

head = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
dir = '/Users/mac/Desktop/毕设/webspider/'

def func():
    # 加载论文源网页
    addi = []
    fileCounts = 1
    for root in roots:
        html = requests.get(root, headers=head)
        html.encoding = "GB2312"
        sites = re.findall('<div class="title">(.*?)</div>', html.text, re.S)
        for site in sites:
            # print(site)
            s = re.findall('<a href="(.*?)" target="_blank">', site, re.S)
            for ss in s:
                addi.append(ss)
    # 加载论文
    for site in addi:
        html = requests.get(site, headers=head)
        html.encoding = "GB2312"
        label = re.findall('<p>(.*?)</p>', html.text, re.S)

        fileName = dir + str(fileCounts) + '.txt'
        doc = open(fileName, 'w')
        print('file counts:%d'%(fileCounts))

        for each in label:
            raw = each.lstrip().rstrip();
            pattern = re.compile(r'<[^>]+>', re.S)
            result = pattern.sub('', raw)
            print(result, file=doc)

        doc.close()
        fileCounts = fileCounts + 1


if __name__ == '__main__':
    func()