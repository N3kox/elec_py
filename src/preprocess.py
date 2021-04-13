# -*- coding:UTF-8 -*-
from webSpider.src.utils import *
from py2neo import Node, Relationship, Graph


# 4.8 another graph on importing
def anotherGraphParser():
    f = jsonReader("all_format")
    graph = dbConn()
    nodeMap = {}
    staffNameSet = getSetByLabelAndProperty("员工", "姓名")
    detailedTypeNameSet = getSetByLabelAndProperty("设备型号", "型号")
    companyNameSet = getSetByLabelAndProperty("运维商", "所属地市")
    equipmentCodeSet = getSetByLabelAndProperty("设备", "设备编码")
    routeNameSet = getSetByLabelAndProperty("电站线路", "变电站名称")
    manufactorNameSet = getSetByLabelAndProperty("生产厂家", "生产厂家")
    classNameSet = getSetByLabelAndProperty("班组", "name")
    countryNameSet = getSetByLabelAndProperty("制造国家", "name")
    equipmentNameMap = {'asset_number': '资产编号',
                        'equipment_status': '设备状态',
                        'Phase': '相别',
                        'device_id': '设备ID',
                        'nature_assets': '资产性质',
                        'equipment_code': '设备编码',
                        'voltage_level_code': '电压等级代码',
                        'date_of_manufacture': '出厂日期',
                        'commissioning_date': '投运日期',
                        'registration_time': '登记时间',
                        'euipment_increase_mode': '设备增加方式',
                        'voltage_level': '电压等级',
                        'PM_code': 'PM编码',
                        'Phase_num': '相数',
                        'function_location': '功能位置',
                        'operation_library_id': '电器铭牌运行库ID',  # tbd
                        'name': '设备名称',
                        'operation_number': '运行编号',
                        'latest_commissioning_date': 'latest_commissioning_date',
                        'factory_number': '工程编号',
                        'remarks': 'remarks',
                        'professional_calssification': '专业分类'}
    relationshipList = []
    relationshipNameMap = {'*型号': '设备型号',
                           '*生产厂家': '生产厂家',
                           '制造国家': '制造国家',
                           '设备类型名称': '设备类型',
                           '*变电站名称': '变电站名称',
                           '*维护班组': '维护班组',
                           '所属地市': '所属地市',
                           '设备主人': '设备主人'}
    for r in f:
        # node parser
        if isNode(r):
            p = r["properties"]
            node = None
            if nodeLabelEquals(r, "设备主人"):
                # continue
                if p["name"] not in staffNameSet:
                    staffNameSet.add(p["name"])
                    node = Node("员工", **{"姓名": p["name"]})
            elif nodeLabelEquals(r, "*型号"):
                # continue
                if p["name"] not in detailedTypeNameSet:
                    detailedTypeNameSet.add(p["name"])
                    node = Node("设备型号", **{"型号":p["name"]})
            elif nodeLabelEquals(r, "运维单位"):
                # continue
                if p["name"] not in companyNameSet:
                    companyNameSet.add(p["name"])
                    node = Node("运维商", **{"所属地市":p["name"]})
            elif nodeLabelEquals(r, "*设备名称"):
                # continue
                if "equipment_code" in p:
                    if p["equipment_code"] not in equipmentCodeSet:
                        equipmentCodeSet.add(p["equipment_code"])
                        node = Node("设备")
                        for key in p:
                            if key in equipmentNameMap:
                                node[equipmentNameMap[key]] = p[key]
                            else:
                                node[key] = p[key]
                else:
                    node = Node("设备类型")
                    node['name'] = p['name']
                    node['类型编号'] = p['equipment_type_code']

            elif nodeLabelEquals(r, "*变电站名称"):
                # 电站线路
                if p["name"] not in routeNameSet:
                    routeNameSet.add(p['name'])
                    node = Node("电站线路")
                    node["变电站名称"] = p['name']
                    node['变电站id'] = p['station_id']
                    node['变电站电压等级'] = p['power_station_voltage_level']
            elif nodeLabelEquals(r, "*生产厂家"):
                if p["name"] not in manufactorNameSet:
                    manufactorNameSet.add(p["name"])
                    node = Node("生产厂家")
                    node["生产厂家"] = p['name']
            elif nodeLabelEquals(r, "*维护班组"):
                if p["name"] not in classNameSet:
                    classNameSet.add(p["name"])
                    node = Node("班组")
                    node["name"] = p["name"]
            elif nodeLabelEquals(r, "制造国家"):
                if p['name'] not in countryNameSet:
                    countryNameSet.add(p['name'])
                    node = Node("制造国家")
                    node["name"] = p['name']
            else:
                print("unknown node mention")
            if node is not None:
                # graph.create(node)
                nodeMap[r['id']] = node
        else:
            if r['start']['id'] in nodeMap and r['end']['id'] in nodeMap:
                rel = Relationship(nodeMap[r['start']['id']], relationshipNameMap[r['label']], nodeMap[r['end']['id']])
                relationshipList.append(rel)
    for rel in relationshipList:
        graph.create(rel)
    print("another Graph parser done")


# 4.1 设备台账.csv to neo4j done
# 4.8 重构，适应新增数据更改实体划分
"""
设备台账csv拆分重构
node : 设备，电站线路，班组，企业，专业分类，生产厂家，设备型号

变电站名称4 & 站线名称16 -> 电站线路
维护班组7 -> 维护班组
设备主人8 -> 设备主人
专业分类22 & 设备类型编码23 -> 专业分类
生产厂家29 -> 生产厂家
型号30 -> 设备型号
所属城市19 & 运维单位28 & 资产单位33 -> 企业
其余 -> 设备
"""
def devicesHelper():
    f = csvReader("设备台账")
    graph = dbConn()
    first = 0
    keys = []
    locNameIndex = 4
    locNameRepeatIndex = 16

    teamNameIndex = 7
    ownerNameIndex = 8
    builderIndex = 29

    detailedTypeIndex = 30

    companyNameIndex = 19
    maintainIndex = 28
    assetCompanyIndex = 33
    countryIndex = 24

    deviceTypeIndex = 2
    deviceTypeCodeIndex = 23

    s = {locNameIndex, teamNameIndex, locNameIndex, companyNameIndex, ownerNameIndex, locNameRepeatIndex, maintainIndex, builderIndex, assetCompanyIndex, detailedTypeIndex, countryIndex, deviceTypeIndex, deviceTypeCodeIndex};
    rel = []
    devices = []

    detailedTypeDict = getMapByLabelAndProperty("设备型号", "型号")
    builderDict = getMapByLabelAndProperty("生产厂家", "生产厂家")
    countryDict = getMapByLabelAndProperty("制造国家", '制造国家')
    deviceTypeDict = getMapByLabelAndProperty('设备类型', 'name')
    locDict = getMapByLabelAndProperty("电站线路", "变电站名称")
    teamDict = getMapByLabelAndProperty("班组", "name")
    companyDict = getMapByLabelAndProperty("运维商", "所属地市")
    ownerDict = getMapByLabelAndProperty("员工", '姓名')

    for row in f:
        if first == 0:
            first = 1;
            for key in row:
                keys.append(key if key[0] != '*' else key[1:])
        else:
            deviceNode = Node("设备", name=str(row[0]))
            for i, val in enumerate(row):
                if i not in s:
                    # deviceNode[keys[i]] = val if len(val) > 0 else 'NULL'
                    deviceNode[keys[i]] = val
            devices.append(deviceNode)

            if row[locNameIndex] not in locDict:
                params = {}
                params[keys[locNameIndex]] = row[locNameIndex]
                params[keys[locNameRepeatIndex]] = row[locNameRepeatIndex]
                locNode = Node("电站线路", **params)
                locDict[row[locNameIndex]] = locNode
                rel.append(Relationship(deviceNode, "变电站名称", locNode))
            else:
                rel.append(Relationship(deviceNode, "变电站名称", locDict[row[locNameIndex]]))

            if row[teamNameIndex] not in teamDict:
                params = {}
                params["name"] = row[teamNameIndex]
                teamNode = Node('班组', **params)
                teamDict[row[teamNameIndex]] = teamNode
                rel.append(Relationship(deviceNode, "维护班组", teamNode))
            else:
                rel.append(Relationship(deviceNode,'维护班组', teamDict[row[teamNameIndex]]))

            # device division
            # if row[typeNameIndex] not in divisionDict.keys():
            #     params = {}
            #     params[keys[typeNameIndex]] = row[typeNameIndex]
            #     params[keys[typeCodeIndex]] = row[typeCodeIndex]
            #     divNode = Node("专业", **params)
            #     divisionDict[row[typeNameIndex]] = len(division)
            #     division.append(divNode)
            #     rel.append(Relationship(deviceNode, '专业分类', divNode))
            # else:
            #     rel.append(Relationship(deviceNode, '专业分类', division[divisionDict[row[typeNameIndex]]]))

            if len(row[ownerNameIndex]) > 0:
                if row[ownerNameIndex] not in ownerDict:
                    params = {}
                    params[keys[ownerNameIndex]] = row[ownerNameIndex]
                    ownerNode = Node("员工", **params)
                    ownerDict[row[ownerNameIndex]] = ownerNode
                    rel.append(Relationship(deviceNode, '设备主人', ownerNode))
                else:
                    rel.append(Relationship(deviceNode, '设备主人', ownerDict[row[ownerNameIndex]]))

            if row[builderIndex] not in builderDict:
                params = {}
                params[keys[builderIndex]] = row[builderIndex]
                builderNode = Node("生产厂家", **params)
                builderDict[row[builderIndex]] = builderNode
                rel.append(Relationship(deviceNode, '生产厂家', builderNode))
            else:
                rel.append(Relationship(deviceNode, '生产厂家', builderDict[row[builderIndex]]))

            if row[detailedTypeIndex] not in detailedTypeDict:
                params = {}
                params[keys[detailedTypeIndex]] = row[detailedTypeIndex]
                detailedTypeNode = Node('设备型号', **params)
                detailedTypeDict[row[detailedTypeIndex]] = detailedTypeNode
                rel.append(Relationship(deviceNode, '设备型号', detailedTypeNode))
            else:
                rel.append(Relationship(deviceNode, '设备型号', detailedTypeDict[row[detailedTypeIndex]]))

            if row[companyNameIndex] not in companyDict:
                params = {}
                params[keys[companyNameIndex]] = row[companyNameIndex]
                params[keys[maintainIndex]] = row[maintainIndex]
                params[keys[assetCompanyIndex]] = row[assetCompanyIndex]
                companyNode = Node('运维商', **params)
                companyDict[row[companyNameIndex]] = companyNode
                rel.append(Relationship(deviceNode, '所属地市', companyNode))
            else:
                rel.append(Relationship(deviceNode,'所属地市', companyDict[row[companyNameIndex]]))

            if row[countryIndex] not in countryDict:
                countryNode = Node('制造国家', **{'name': row[countryIndex]})
                countryDict[row[countryIndex]] = countryNode
                rel.append(Relationship(deviceNode, '制造国家', countryNode))
            else:
                rel.append(Relationship(deviceNode, '制造国家', countryDict[row[countryIndex]]))

            if row[deviceTypeIndex] not in deviceTypeDict:
                deviceTypeNode = Node("设备类型")
                deviceTypeNode['name'] = row[deviceTypeIndex]
                deviceTypeNode['类型编号'] = row[deviceTypeCodeIndex]
                rel.append(Relationship(deviceNode, '设备类型', deviceTypeNode))
            else:
                rel.append(Relationship(deviceNode, '设备类型', deviceTypeDict[row[deviceTypeIndex]]))
    # create nodes and relations
    for r in rel:
        graph.create(r)

    print("deviceHelper done")


# 标准工作任务单与工单编号一致
def staffHelper():
    a = csvReader("标准工作任务单")
    b = csvReader("工单")
    c = csvReader("工作票")
    d = csvReader("修饰记录")
    l = [a, b, c, d]
    staffSet = []
    for f in l:
        locIndex = -1
        indexSet = []
        for i, row in enumerate(f):
            if i == 0:
                for j, key in enumerate(row):
                    if "市" in key:
                        locIndex = j
                    if "人" in key and "人数" not in key:
                        indexSet.append(j)
            else:
                if(locIndex < 0):
                    break
                for j in indexSet:
                    couple = (row[locIndex], row[j])
                    found = False
                    for ss in staffSet:
                        if(ss[0] == couple[0] and ss[1] == couple[1]):
                            found = True
                            break
                    if found == False:
                        staffSet.append(couple)

    for couple in staffSet:
        if len(couple[0]) == 0 or len(couple[1]) == 0:
            continue
        pa = {}
        pa["所属地市"] = couple[0]
        pb = {}
        pb["姓名"] = couple[1]
        city = dbConn().nodes.match("运维商", **pa).first()
        # 如果city不存在，则staff必不存在，新增rel
        if city is None:
            city = Node("运维商", **pa)
            staff = Node("员工", **pb)
            dbConn().create(Relationship(staff, "就职", city))
        # 如果city存在staff不存在，新增rel
        # 如果city存在staff存在，staff可能为重名其他地区的人，检测rel后再决定是否新增
        # print(city['所属地市'])
        else:
            staff = dbConn().nodes.match("员工", **pb).first()
            if staff is None:
                staff = Node("员工", **pb)
                dbConn().create(Relationship(staff, "就职", city))
            elif dbConn().match_one((staff, city), r_type="就职") is None:
                dbConn().create(Relationship(staff, "就职", city))
    print("staffHelper done")


def isRelated(nodeA, nodeB, relName):
    return True if len(dbConn().match((nodeA, nodeB), r_type=relName)) > 0 else False


# 4.6 partA done
"""
所属地市2 -> 运维商
电站线路3(需parse) -> 电站线路
编制人7 -> 人员 （运维商与人员进行关系检索以防重名）
工作内容1 -> [消除编号, 具体电站线路, 概述, 详述]
"""
def partA():
    graph = dbConn()
    f = csvReader("标准工作任务单")
    cityIndex = 2
    routeIndex = 3
    staffIndex = 7
    workDetailsIndex = 1
    skipList = [6, workDetailsIndex, cityIndex, routeIndex, staffIndex]
    nameList = []
    routeList = {}
    routeWordSkipList = list('一二三四五六七八九十支')
    rel = []
    for route in graph.nodes.match("电站线路"):
        routeList[route['站线名称']] = route

    for i, row in enumerate(f):
        if i == 0:
            for val in row:
                nameList.append(val)
        else:
            ticket_a_node = Node("标准工作任务单")
            for j, val in enumerate(row):
                if j not in skipList:
                    ticket_a_node[nameList[j]] = val

            projList = (row[workDetailsIndex][5:]).split('，')
            ticket_a_node["消除编号"] = projList[0][3:]
            ticket_a_node["具体地点"] = projList[1]
            ticket_a_node["任务概述"] = projList[2]
            ticket_a_node["任务详述"] = ','.join(projList[3:])
            # print(ticket_a_node["任务详述"])
            # route name similarity compare and relate
            routeName = row[routeIndex]
            l = len(routeName)
            while l > 2 and routeName[l - 1] in routeWordSkipList:
                l -= 1
            routeProperties = {"站线名称": routeName[:l]}
            routeNode = nodeGetOrNew("电站线路", **routeProperties)
            rel.append(Relationship(ticket_a_node, "任务位置", routeNode))

            cityNode = graph.nodes.match("运维商", 所属地市=row[cityIndex]).first()
            staffNodeList = graph.nodes.match("员工", 姓名=row[staffIndex])
            for staffNode in staffNodeList:
                if isRelated(staffNode, cityNode, "就职") is True:
                    # print(staffNode, cityNode)
                    rel.append(Relationship(ticket_a_node, "任务单所属公司", cityNode))
                    rel.append(Relationship(ticket_a_node, "任务单编制人", staffNode))
                    break;

    for r in rel:
        graph.create(r)
    print("partA done")



# partB
def partB():
    graph = dbConn()
    f = csvReader("工单")
    coidIndex = 0
    cityIndex = 3
    routeIndex = 4
    staffIndex = 7
    skipList = [coidIndex, cityIndex, staffIndex, routeIndex]
    titleList = []
    rel = []
    for i, row in enumerate(f):
        if i == 0:
            for val in row:
                titleList.append(val)
        else:
            ticket_b_node = Node("工单")
            for j, val in enumerate(row):
                if j not in skipList:
                    ticket_b_node[titleList[j]] = val

            # link to partA
            nodeA = graph.nodes.match("标准工作任务单", 编号=row[coidIndex]).first()
            if nodeA != None:
                rel.append(Relationship(ticket_b_node, "对应", nodeA))
            cityNode = graph.nodes.match("运维商", 所属地市=row[cityIndex]).first()
            staffNodeList = graph.nodes.match("员工", 姓名=row[staffIndex])
            for staffNode in staffNodeList:
                if isRelated(staffNode, cityNode, "就职") is True:
                    rel.append(Relationship(ticket_b_node, "工单所属公司", cityNode))
                    rel.append(Relationship(ticket_b_node, "工单编制人", staffNode))
                    break;
            routeProperties = {"站线名称": row[routeIndex]}
            routeNode = nodeGetOrNew("电站线路", **routeProperties)
            rel.append(Relationship(ticket_b_node, "工单任务位置", routeNode))

    for r in rel:
        graph.create(r)
    print("partB done")


# partC
def partC():
    graph = dbConn()
    f = csvReader("工作票")
    obj_set = []
    workLocIndex = 4
    cityAIndex = 5
    cityBIndex = 6

    staffAIndex = 8
    staffBIndex = 9
    staffCIndex = 15
    staffDIndex = 17
    staffEIndex = 20

    ticketFormationIndex = 10
    skipList = [0, workLocIndex, cityAIndex, cityBIndex, staffAIndex, staffBIndex, staffCIndex, staffDIndex, staffEIndex]
    titleList = []
    rel = []
    for i, row in enumerate(f):
        if i == 0:
            for val in row:
                titleList.append(val)
        else:
            # obj_id 去重
            if row[1] in obj_set:
                continue
            else:
                obj_set.append(row[1])

            ticket_c_node = Node("工作票")
            for j, val in enumerate(row):
                if j not in skipList:
                    ticket_c_node[titleList[j]] = val

            ticket_c_node["key_id"] = row[ticketFormationIndex].split('-')[-1]
            workLocNode = nodeGetOrNew("电站线路", **{"站线名称":row[workLocIndex]})
            cityNode = nodeGetOrNew("运维商", **{"所属地市":row[cityAIndex]})
            staffANode = nodeGetOrNew("员工", **{"姓名":row[staffAIndex]})
            staffBNode = nodeGetOrNew("员工", **{"姓名":row[staffBIndex]})
            staffCNode = nodeGetOrNew("员工", **{"姓名":row[staffCIndex]})
            staffDNode = nodeGetOrNew("员工", **{"姓名":row[staffDIndex]})

            rel.append(Relationship(ticket_c_node, "工作票位置", workLocNode))
            rel.append(Relationship(ticket_c_node, "工作票所属公司", cityNode))
            rel.append(Relationship(ticket_c_node, "工作负责人", staffANode))
            rel.append(Relationship(ticket_c_node, "签发人", staffBNode))
            rel.append(Relationship(ticket_c_node, "许可人", staffCNode))
            rel.append(Relationship(ticket_c_node, "完工负责人", staffDNode))

            # 处理班组人数可能大于1的问题
            # staffENode = nodeGetOrNew("员工", **{"姓名":row[staffEIndex]})
            # rel.append(Relationship(ticket_c_node, "工作班组人员", staffENode))
            classStaffs = row[staffEIndex].split("-")
            for se in classStaffs:
                senode = nodeGetOrNew("员工", **{"姓名" : se})
                rel.append(Relationship(ticket_c_node, "工作班组人员", senode))

    for r in rel:
        graph.create(r)
    print("partC done")


def partD():
    graph = dbConn()
    f = csvReader("修饰记录")
    cityIndex = 1
    deviceLocIndex = 3
    ticketFormationIndex = 6
    staffAIndex = 12
    staffBIndex = 15

    skipList = [cityIndex, deviceLocIndex, staffAIndex, staffBIndex]
    titleList = []
    rel = []
    for i, row in enumerate(f):
        if i == 0:
            for val in row:
                titleList.append(val)
        else:
            ticket_d_node = Node("修饰记录")
            for j, val in enumerate(row):
                if j not in skipList:
                    ticket_d_node[titleList[j]] = val
            key_id = row[ticketFormationIndex].split("-")[-1]
            ticket_d_node["key_id"] = key_id
            cityNode = nodeGetOrNew("运维商", **{"所属地市" : row[cityIndex]})
            deviceLocNode = nodeGetOrNew("电站线路", **{"站线名称" : row[deviceLocIndex]})
            staffANode = nodeGetOrNew("员工", **{"姓名" : row[staffAIndex]})
            staffBNode = nodeGetOrNew("员工", **{"姓名" : row[staffBIndex]})
            rel.append(Relationship(ticket_d_node, "所属地市", cityNode))
            rel.append(Relationship(ticket_d_node, "修饰地点", deviceLocNode))
            rel.append(Relationship(ticket_d_node, titleList[staffAIndex], staffANode))
            rel.append(Relationship(ticket_d_node, titleList[staffBIndex], staffBNode))

            ticket_c_node = graph.nodes.match("工作票", key_id=key_id).first()
            if ticket_c_node is not None:
                # print(ticket_c_node)
                rel.append(Relationship(ticket_d_node, "对应", ticket_c_node))

    for r in rel:
        # print(r)
        graph.create(r)
    print("partD done")


# 4.6 修饰记录属性更新
def d_update():
    graph = dbConn()
    f = csvReader("修饰记录")
    ticketFormationIndex = 6
    for i, row in enumerate(f):
        if i != 0:
            id = row[0]
            if len(row[ticketFormationIndex]) == 0:
                continue
            key = row[ticketFormationIndex].split("-")[-1]
            node = graph.nodes.match("修饰记录", **{"修试记录ID":id}).first()
            if node is not None:
                node.update({"key_id": key})
                graph.push(node)


def locationHelper():
    graph = dbConn()
    updateList = []
    for node in graph.nodes.match("电站线路"):
        if "站线名称" not in node:
            node["站线名称"] = node["变电站名称"]
            updateList.append(node)

        if "变电站名称" not in node:
            node["变电站名称"] = node["站线名称"]
            updateList.append(node)

    for n in updateList:
        graph.push(n)


def init():
    anotherGraphParser()
    devicesHelper()
    staffHelper()
    partA()
    partB()
    partC()
    partD()
    locationHelper()
    print("init done")

init()