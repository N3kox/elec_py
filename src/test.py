# -*- coding:UTF-8 -*-
import sys
import csv
import py2neo
from py2neo import Node, Relationship, Graph, NodeMatcher, PropertyDict
from src.utils import *

print(py2neo.__version__)

# a = db.match((""),r_type="就职")
# name = "国网天津检修公司"
# r = 'MATCH (a:`运维商`) WHERE a.所属地市="%s" RETURN a' % name
# entity_node = db.run(r)
# for node in entity_node:
#     print(node)
#     triple = node.get('a')
#     for r in triple:
#         tail = triple[r]
#         print(name, r, tail)

# b = db.nodes.match().where("_.name='bob'")
# c = NodeMatcher(db).match("People", name='alice').first()
# a = db.nodes.match().where("_.name='alice'")
# print(a)
# db.create(Node("People", name = "alice"))
# print(db.nodes.match("People", name="alice").first())

# select all
# a = db.nodes.match("生产厂家")
# for aa in a:
#     for k in aa.keys():
#         print("%s\t\t%s" %(k, aa[k]))
#
# def func(a, b, r_type):
#     for aa in a:
#         for bb in b:
#             rel = db.match((aa, bb), r_type="就职")
#             if len(rel) > 0:
#                 return rel.first().start_node, rel.first().end_node
#     return None
#
#
# key = "城南-运维检修部(检修分公司)(变一)-2020050016".split('-')[-1]
# print(key)

f = jsonReader("all_format")
for row in f:
    if isNode(row):
        if nodeLabelEquals(row, "*设备名称") and "equipment_code" not in row['properties']:
            print(row)
    else:
        print(row)