# -*- coding = UTF-8 -*-
from collections import defaultdict
import math
import operator
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from src.mission_slicer import work_detail_parser_ltp, work_detail_parser_jieba

"""
函数说明:创建数据样本
Returns:
    da + db - 实验样本切分的词条
    classVec - 类别标签向量
"""


def loadDataSet():
    da, db = work_detail_parser_jieba()
    classVec = [0, 1, 0, 1, 0, 1]
    return da + db, classVec


"""
函数说明：特征选择TF-IDF算法
Parameters:
     list_words:词列表
Returns:
     dict_feature_select:特征选择词字典
"""


def feature_select(list_words):
    # 总词频统计
    doc_frequency = defaultdict(int)
    for word_list in list_words:
        for i in word_list:
            doc_frequency[i] += 1

    # 计算词TF
    word_tf = {}
    for i in doc_frequency:
        word_tf[i] = doc_frequency[i] / sum(doc_frequency.values())

    # 计算词IDF
    doc_num = len(list_words)
    word_idf = {}
    word_doc = defaultdict(int)
    for i in doc_frequency:
        for j in list_words:
            if i in j:
                word_doc[i] += 1
    for i in doc_frequency:
        word_idf[i] = math.log(doc_num / (word_doc[i] + 1))

    # 计算词TF*IDF
    word_tf_idf = {}
    for i in doc_frequency:
        word_tf_idf[i] = word_tf[i] * word_idf[i]

    # 字典按值降序排序
    dict_feature_select = sorted(word_tf_idf.items(), key=operator.itemgetter(1), reverse=True)
    return dict_feature_select


if __name__ == '__main__':
    data_list, label_list = loadDataSet()
    features = feature_select(data_list)
    for f in features:
        print(f)