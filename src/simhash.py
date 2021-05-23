# -*- coding : utf-8 -*-
import jieba
import jieba.analyse
import numpy as np
from utils import getStopWordPath


class SimHash(object):
    def simHash(self, content):
        seg = jieba.cut(content)
        # jieba基于TF-IDF提取关键词
        jieba.analyse.set_stop_words(getStopWordPath())
        keyWords = jieba.analyse.extract_tags("|".join(seg), topK=5, withWeight=True, allowPOS=('ns', 'n', 'nr'))
        keyList = []
        for feature, weight in keyWords:
            print('weight: {}'.format(weight))
            # weight = math.ceil(weight)
            weight = int(weight)
            binstr = self.string_hash(feature)
            temp=[]
            for c in binstr:
                if (c == '1'):
                    temp.append(weight)
                else:
                    temp.append(-weight)
            keyList.append(temp)
        listSum = np.sum(np.array(keyList), axis = 0)
        if (keyList == []):
            return '00'
        simhash = ''
        for i in listSum:
            if (i>0):
                simhash = simhash + '1'
            else:
                simhash = simhash + '0'

        return simhash


    def string_hash(self, source):
        if source == "":
            return 0
        else:
            x = ord(source[0]) << 7
            m = 1000003
            mask = 2**128 - 1
            for c in source:
                x = ((x*m)^ord(c)) & mask
            x ^= len(source)
            if x == -1:
                x = -2
            x = bin(x).replace('0b', '').zfill(64)[-64:]
            # print('strint_hash: %s, %s'%(source, x))
            return str(x)


    def getDistance(self, hashstr1, hashstr2):
        # 计算simhash的汉明距离
        length = 0
        for index, char in enumerate(hashstr1):
            if char == hashstr2[index]:
                continue
            else:
                length += 1
        return length


# TODO : simhash持久化与
if __name__ == '__main__':
    simhash = SimHash()

    s1 = simhash.simHash('adss补修绑扎线松散')
    s2 = simhash.simHash('adss接线盒脱落')
    dis = simhash.getDistance(s1, s2)
    print('dis: {}'.format(dis))