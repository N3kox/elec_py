# -*- coding:UTF-8 -*-

import py2neo
import jieba
import jieba.analyse
import jieba.posseg
from utils import *

print(py2neo.__version__)

s = ""
j = jsonRead("金具")
if type(j) is list:
    j = j[0]

for k in j:
    for v in j[k]:
        s += v

# print(getStopWordPath())
jieba.analyse.set_stop_words(getStopWordPath())
keywords = jieba.analyse.textrank(s, topK=5, withWeight=True, allowPOS=('ns', 'n', 'nr'))
for item in keywords:
    print(item[0], item[1])