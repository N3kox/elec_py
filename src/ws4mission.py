# -*- coding: UTF-8 -*-
import requests
import src.mission_slicer as slicer
import src.mySearch as mySearch
from utils import pickleWrite, pickleReader, readStopSet

head = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
dir = r"E:\毕设\data\ws4mission\\"
directSearchDir = 'https://baike.baidu.com/item/'
mumbleSearchDir = 'https://baike.baidu.com/search/none?word=[wordFiller]&pn=0&rn=10&enc=utf8'


def directSearch(str):
    html = requests.get(directSearchDir + str, headers=head)
    html.encoding = 'UTF-8'
    return html.text


def mumbleSearch(str):
    html = requests.get(mumbleSearchDir.replace('[wordFiller]', str), headers=head)
    html.encoding = 'UTF-8'
    return html.text


def readMission():
    wa, pa = slicer.work_summary_parser_ltp()
    # 初始化停用词(百度停用词表)
    stopSet = readStopSet()
    wa_next = set()
    for i in range(len(wa)):
        a = wa[i]
        b = pa[i]
        for j in range(len(a)):
            if b[j] == 'n' and a[j] not in stopSet:
                wa_next.add(a[j])
    return wa_next


def entitySearch(entity_list):
    emap = {}
    for entity in entity_list:
        ds = directSearch(entity)
        # 精准查询成功
        if not mySearch.judge_direct_search_error(ds):
            entity_map = mySearch.direct_search_map(entity)
            emap[entity] = 'direct'
            pickleWrite(entity, entity_map)
        # 精准查询失败,尝试模糊搜索
        else:
            entity_map_list = mySearch.mumble_search_map(entity)
            if entity_map_list is None:
                # emap[entity] = 'none'
                continue
            emap[entity] = 'mumble'
            pickleWrite(entity, entity_map_list)
    pickleWrite('entity_index', emap)


def getExplanation(entity):
    emap = pickleReader('entity_index')
    if emap is None:
        print("entity map hasn't been created!!")
    elif entity in emap:
        content = pickleReader(entity)
        print(content)
    else:
        print("nothing")


def missionParser(textList):
    for text in textList:
        wa, pa = slicer.origin_text_parser_ltp(text)
        stopSet = readStopSet()
        



if __name__ == '__main__':
    getExplanation('adss')