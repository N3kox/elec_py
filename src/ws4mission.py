# -*- coding: UTF-8 -*-
import requests
import webSpider.src.mission_slicer as slicer
import webSpider.src.mySearch as mySearch
from utils import pickleWrite, pickleRead, getStopSet
from webSpider.src.static import directSearchDir, mumbleSearchDir, head

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
    stopSet = getStopSet()
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
    emap = pickleRead('entity_index')
    if emap is None:
        print("entity map hasn't been created!!")
    elif entity in emap:
        content = pickleRead(entity)
        print(content)
    else:
        print("nothing")


def missionTextParser(textList):
    wa, pa = slicer.text_work_summary_parser_ltp(textList)
    stopSet = getStopSet()
    wa_next = set()
    for i in range(len(wa)):
        a = wa[i]
        b = pa[i]
        for j in range(len(a)):
            if a[j] not in stopSet and b[j] == 'n':
                wa_next.add(a[j])
    return wa_next


if __name__ == '__main__':
    getExplanation('adss')