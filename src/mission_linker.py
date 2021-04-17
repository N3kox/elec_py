# -*- coding : utf-8 -*-

import json
from py2neo import Node, Relationship
from utils import dbConn, jsonWrite


def db_mission_link():
    kv = {}
    keys = []
    vals = []
    g = dbConn()
    rels = g.match(r_type='对应')
    for rel in rels:
        sa = set(rel.start_node.labels)
        sb = set(rel.end_node.labels)
        if '工单' in sa and '标准工作任务单' in sb:
            kv[rel.end_node['任务概述']] = rel.start_node['任务内容']
            keys.append(rel.end_node['任务概述'])
            vals.append(rel.start_node['任务内容'])
    jsonWrite('mission_links', kv)
    jsonWrite('mission_links_start', keys)
    jsonWrite('mission_links_end', vals)


if __name__ == '__main__':
    db_mission_link()