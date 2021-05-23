# -*- coding = UTF-8 -*-
import jieba
import jieba.analyse
from utils import jsonRead, getStopWordPath, jsonWrite


def readEntityIndex():
    ind = jsonRead("entity_index")
    res = []
    for k in ind:
        res.append(k)
    return res


def calEntityKeywords(s, thr):
    j = jsonRead(s)
    ss = ""
    if type(j) is list:
        j = j[0]
    for k in j:
        for v in j[k]:
            ss += v
    keywords = jieba.analyse.textrank(ss, topK=5, withWeight=True, allowPOS=('ns', 'n', 'nz', 'nt', 'un'))
    res = {}
    for item in keywords:
        if item[1] >= thr:
            res[item[0]] = item[1]
    return res


# 构建keywords映射与反向映射
if __name__ == '__main__':
    l = readEntityIndex()
    jieba.analyse.set_stop_words(getStopWordPath())
    threshold = 0.1
    res = {}
    for n in l:
        res[n] = calEntityKeywords(n, threshold)
    if jsonWrite("entity_keywords", res):
        print("keywords 映射构建完成")
    rres = {}
    for n in res:
        for k in res[n]:
            # print(k)
            if k not in rres:
                rres[k] = []
            rres[k].append(n)
    if jsonWrite("entity_keywords_reverse", rres):
        print("keywords 反向映射构建完成")



