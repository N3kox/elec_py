# -*- coding: UTF-8 -*-
import requests
import mission_slicer as slicer
import mySearch as mySearch
from utils import pickleWrite, pickleRead, getStopSet, jsonRead
from static import directSearchDir, mumbleSearchDir, head
from mission_slicer import text_slicer


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


# 使用entities获取
def getExplanationExtension(entities):
    res = []
    j1 = jsonRead("entity_index")
    j2 = jsonRead("entity_keywords_reverse")
    # full match
    for e in entities:
        for item in j1:
            if e == item:
                tup = [item, e]
                if tup not in res:
                    res.append(tup)
        for item in j2:
            if e == item:
                for v in j2[item]:
                    tup = [v, e]
                    if tup not in res:
                        res.append(tup)
    return res


def getExplanation(entity):
    emap = pickleRead('entity_index')
    if emap is None:
        return None
    elif entity in emap:
        content = pickleRead(entity)
        return {entity: content}
    else:
        return None


def getResource(entity):
    j = jsonRead(entity)
    if j is None:
        return None
    return j


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


def termSearch(text):
    slist = text_slicer(text)
    return getExplanationExtension(slist)


def termSearchExact(text):
    j = jsonRead(text)
    return j


def solutionSearch(text):
    j = jsonRead("mission_links")
    slist = text_slicer(text)
    res = []
    for s in slist:
        for k in j:
            if s in k:
                a = [k, j[k]]
                if a not in res:
                    res.append(a)
    return res


if __name__ == '__main__':
    entitySearch(missionTextParser(["混凝土杆存在异物"]))
