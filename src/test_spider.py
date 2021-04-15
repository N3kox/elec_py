# -*- coding : UTF-8 -*-
import re
import requests
from mySearch import direct_search_map
from baike import Baike, getBaike

head = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
root = 'https://baike.baidu.com/item/'

def func():
    html = requests.get(root + 'adss接线盒', headers=head)
    html.encoding = "UTF-8"
    fileName = '/Users/mac/Desktop/毕设/数据/test.txt'
    f = open(fileName, 'w')
    print(html.text, file = f)


if __name__ == '__main__':
    str = getBaike('a接线盒')
    print(str)
    # for i, row in enumerate(str):
    #     print(getBaike('adss', no=[1,[i]]))