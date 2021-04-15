# -*- coding:UTF-8 -*-

import csv
import json
import pickle

from py2neo import Node, Relationship, Graph

dir = r"E:\毕设\data\\"
pklDir = dir + 'ws4mission\pickles\\'
stopDir = dir + 'stopwords\\'
stopFileDir = stopDir + 'baidu_stopwords.txt'


def csvReader(fileName):
    print(dir+fileName+".csv")
    return csv.reader(open(dir + fileName + ".csv", "r", encoding="UTF-8-sig"))


def dbConn():
    testGraph = Graph(
        address=('localhost', '7687'),
        auth=("neo4j", "shuffleralt1999")
    )
    return testGraph


# return the existing node or a new one which has been created
def nodeGetOrCreate(label, **properties):
    graph = dbConn()
    nodeList = graph.nodes.match(label, **properties)
    if len(nodeList) > 0:
        # print("found")
        return nodeList.first()
    n = Node(label, **properties)
    graph.create(n)
    return n


# return the existing node or a new one which has not been created
def nodeGetOrNew(label, **properties):
    graph = dbConn()
    nodeList = graph.nodes.match(label, **properties)
    if len(nodeList) > 0:
        return nodeList.first()
    return Node(label, **properties)


# format neo4j json file
def jsonFormat(fileName):
    with open(dir + fileName + '.json', 'r', encoding='utf-8') as f1, open(dir + fileName + '_format.json', 'w', encoding='utf-8') as f2:
        f2.write('[')
        f1 = f1.readlines()
        rows = 0
        for i in f1:
            rows += 1
        cur = 0
        for line in f1:
            # if line.find(" ") > 0:
            #     line = line.replace(" ", '')
            if cur != rows - 1:
                f2.writelines(line[:-1] + ',\n')
            else:
                f2.writelines(line)
            cur += 1
        f2.write(']')
    print(fileName + ".json formatted")


# format json reader
def jsonReader(fileName):
    fp = open(dir + fileName + '.json', 'r', encoding='utf-8')
    return json.load(fp)


def isNode(dict):
    if "type" in dict and dict["type"] == 'node':
        return True
    return False


def isRelationship(dict):
    if "type" in dict and dict["type"] == "relationship":
        return True
    return False


def nodeLabelEquals(dict, val):
    if "labels" in dict and val in dict["labels"]:
        return True
    return False


def relationLabelEquals(dict, val):
    if "label" in dict and dict["label"] == val:
        return True
    return False


# def getStaffNameSet():
#     graph = dbConn()
#     s = set()
#     for node in graph.nodes.match("员工"):
#         s.add(node["姓名"])
#     return s

def getSetByLabelAndProperty(labelName, propertyName):
    graph = dbConn()
    s = set()
    for node in graph.nodes.match(labelName):
        s.add(node[propertyName])
    return s


def getMapByLabelAndProperty(labelName, propertyName):
    graph = dbConn()
    m = {}
    for node in graph.nodes.match(labelName):
        m[node[propertyName]] = node
    return m


def getPkl(name):
    return pklDir + name + '.pkl'


def pickleWrite(name, content):
    try:
        # print(name)
        # print(content)
        pf = open(getPkl(name), 'wb')
        pickle.dump(content, pf)
        pf.close()
        return True
    except IOError:
        print("Error:pickle写入失败")
        return False


def pickleReader(name):
    try:
        pf = open(getPkl(name), 'rb')
        content = pickle.load(pf)
        pf.close()
        return content
    except IOError:
        print("Error:pickle读取失败")
        return None


# 停用词表读取
def readStopSet():
    stopFile = open(stopFileDir, 'r', encoding='utf-8')
    stopSet = set()
    for val in stopFile:
        stopSet.add(val)
    return stopSet