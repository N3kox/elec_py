Graph.py
class Edge:
    def __init__(self,nodeA,nodeB,weight):
        self.nodeA = nodeA
        self.nodeB = nodeB
        self.weight = weight

class Node:
    def __init__(self,lemma,score,type):
        self.lemma = lemma
        self.score = score
        self.type = type
Graph_ConstructionV0_4_4_1.py
#coding:utf-8

import copy
import os
import socket

import requests
from random import random

import gensim
import json
from graphviz import Digraph
import datetime
from graphviz import render
from Graph import Node, Edge
import matplotlib.pyplot as plt

from readFile import readRawFile


class GraphForEntityV0_4_4():
    def __init__(self,sentenceDict,rawSentenceDict,all_entity,localIp,port ):
            # indexFile = "包含空句_all_只包含最长实体.json"
            # indexFile = "方位词_all_只包含最长实体.json"
        self.localIp = localIp
        self.port = port
        self.sentenceDict = sentenceDict

        self.rawSentenceDict = rawSentenceDict

        self.Graph = []
        self.nodeDict = dict()
        self.v_v_Co_Dict = dict()
        self.all_entity = all_entity
        # self.wv_from_text = wv_from_text


    def getEntityAndRelationBySeeds(self,seed,entityType,isSeed,seedType,findEntity,findRelation):
        """
        找与seed相连的实体和关系，并将其作为边“边”加入到Graph中。
        :param seed: 种子实体
        :param entityType: 尾实体的类型
        :param isSeed: 是否是种子实体，False：是第二次迭代的结果
        :param seedType: entity or relation
        :param findEntity: 是否找与seed相连的实体
        :param findRelation: 是否找与seed相连的关系
        :return:
        """
        weight = 1
        entityList = []
        relationList = []
        entityTypeList = []  # 初始化与entityType对应的实体列表
        if entityType == 'LOC':
            entityTypeList = self.location_xlore_entity
        elif entityType == 'PER':
            entityTypeList = self.person_xlore_entity
        elif entityType == 'ORG':
            entityTypeList = self.organization_xlore_entity
        elif entityType == 'ALL':
            entityTypeList = self.all_entity

        if seed in self.nodeDict:  # 如果种子已经在nodeDict中
            seedNode = self.nodeDict[seed]  # 去除seedNode
        else:
            if isSeed == True:  # 如果seed是初始种子
                seedNode = Node(seed,1,seedType)  # score设为1
            else:
                seedNode = Node(seed,0,seedType)  # 一般不会走，因为若不是初始种子，则该实体已经在nodeDict登记过
            self.nodeDict[seed] = seedNode

        for sentID in self.sentenceDict:
            sentence = self.sentenceDict[sentID]  # 遍历每个句子
            rawSentence = self.rawSentenceDict[sentID]
            if len(rawSentence) > 100:
                continue
            for item in sentence:
                word = item[0]
                location = word.find("_")
                Numlocation = word.find("#")
                word = word[Numlocation + 1:location]  # 得到每个item的词语
                if word == seed:  # 如果该词与seed一样
                    hasGottenEntity = False
                    hasGottenRel = False
                    relAndEntityHasRel = False
                    relAndEntityHasEntity = False
                    for aItem in sentence:  # 再次遍历该sentence中的item

                        aWord = aItem[0]
                        aLocation = aWord.find("_")
                        aNumlocation = aWord.find("#")
                        clean_word = aWord[aNumlocation + 1:aLocation]


                        if findEntity == True and hasGottenEntity == False and (clean_word in entityTypeList) and aItem[
                            1] > item[1] \
                                and aNumlocation != -1:
                            if aItem[1] - item[1] - len(word) != 0 and relAndEntityHasRel == False:
                                # 如果我们找与seed相连实体，且该item也在entityTypeList中  # 设置这个共现实体要在种子的后面
                                # print(clean_word)
                                if clean_word != seed and abs(aItem[1] - item[1] - len(word)) <= 10:  # 设置两个实体距离不能超过10
                                    entityList.append(clean_word)  # 把该词加入到返回结果entityList中
                                    # print(clean_word)
                                    if clean_word not in self.nodeDict:
                                        entityNode = Node(clean_word, 0, "entity")  # 只要不是原始种子实体，所有实体的score = 0
                                        self.nodeDict[clean_word] = entityNode
                                    else:
                                        entityNode = self.nodeDict[clean_word]
                                    # print(seedNode.lemma, entityNode.lemma)
                                    entityEdge = Edge(seedNode, entityNode, weight)  # 生成seedNode与entityNode的边，权重初始化为1
                                    if self.graphHasEdge(self.Graph, entityEdge) == False:
                                        self.Graph.append(entityEdge)
                                    else:  # 如果该边已经存在，则该边的权重+1
                                        entityEdge = self.graphHasEdge(self.Graph, entityEdge)  # 从Graph中找到这条边
                                        entityEdge.weight += 1
                                        # print('Here')
                                    hasGottenEntity = True  # 只找离实体最近的一个实体
                                    if hasGottenRel == False:
                                        relAndEntityHasEntity = True  # 已经找到尾实体；只要找到尾实体，就不找relation了
                            if aItem[1] - item[1] - len(word) == 0:
                                hasGottenEntity = True  # 只找离实体最近的一个实体
                                if hasGottenRel == False:
                                    relAndEntityHasEntity = True

                        elif findRelation == True and relAndEntityHasEntity == False and 'v' in aWord and aNumlocation == -1 and hasGottenRel == True:
                            relAndEntityHasRel = True  # 已经找到第二个关系，所以不找尾实体

                        elif findRelation == True and relAndEntityHasEntity == False and hasGottenRel == False and 'v' in aWord and aNumlocation == -1:
                            if clean_word != seed and abs(aItem[1] - item[1] - len(word)) <= 10 and isSeed == True \
                                    and aItem[1] > item[1]:  # 限制关系与实体的距离不能超过10  # 限制动词关系必须在种子实体后面 # 只找离实体最近的一个关系
                                if clean_word == '是' or clean_word == '为' or clean_word == '到' \
                                        or clean_word == '来' or clean_word == '使':
                                    # hasGottenRel = True
                                    continue
                                relationList.append(clean_word)
                                if clean_word not in self.nodeDict:
                                    if isSeed == True:
                                        relationNode = Node(clean_word, 1, "relation")  # 直接与实体相连的关系节点的score设置为1
                                    else:
                                        relationNode = Node(clean_word, 0, "relation")  # 不直接与实体相连的关系节点score设置为0
                                    self.nodeDict[clean_word] = relationNode
                                else:  # 如果该边已经存在，则该边的权重+1
                                    relationNode = self.nodeDict[clean_word]
                                # print(seedNode.lemma, relationNode.lemma)
                                relationEdge = Edge(seedNode, relationNode, weight)  # 边的weight初始化为1
                                if self.graphHasEdge(self.Graph, relationEdge) == False:  # 判断该边是否存在，若不存在，在Graph中新增这条边
                                    self.Graph.append(relationEdge)
                                else:
                                    relationEdge = self.graphHasEdge(self.Graph, relationEdge)  # 从Graph中获得该边
                                    relationEdge.weight += 1
                                    # print('Here!!')
                                hasGottenRel = True
                    # break
            # print('----------------------------------')
        return list(set(entityList)),list(set(relationList))

    def graphHasEdge(self,graph,edge):
        node1 = edge.nodeA
        node2 = edge.nodeB
        for i in graph:
            if node1.lemma == i.nodeA.lemma and node2.lemma == i.nodeB.lemma:
                return i
            elif node1.lemma == i.nodeB.lemma and node2.lemma == i.nodeA.lemma:
                return i
        return False


    def getE_A_EdgeWithLemma(self,lemma):
        edgeList = []
        sum = 0
        for edge in self.Graph:
            if (edge.nodeA.lemma == lemma or edge.nodeB.lemma == lemma) and (edge.nodeA.type != edge.nodeB.type):
                edgeList.append(edge)
                sum += edge.weight
                # print(edge.nodeA.lemma, edge.nodeB.lemma, edge.weight)
        return edgeList,sum

    # def computeAm_En(am):
    #     edgeList = getEdgeWithLemma(am)
    #     sum = 0
    #     for edge in edgeList:
    #         if edge.nodeA.lemma == am and edge.nodeB
    #
    def Hypothesis1ForEntity(self,entityNode):
        edgeList,sumForEntity = self.getE_A_EdgeWithLemma(entityNode.lemma)
        s1ForEntity = 0
        for edge in edgeList:
            relationNode = None
            nodeA = edge.nodeA
            nodeB = edge.nodeB
            if nodeA.type == 'relation':
                relationNode = nodeA
            elif nodeB.type == "relation":
                relationNode = nodeB
            edgeList2,sumForRelation = self.getE_A_EdgeWithLemma(relationNode.lemma)
            s1ForEntity += relationNode.score * (edge.weight/sumForRelation)
        # NewEntityNode = copy.deepcopy(entityNode)
        # NewEntityNode.score = s1ForEntity
        return s1ForEntity


    def Hypothesis1ForRelation(self,relationNode):
        edgeList,sumForRelation = self.getE_A_EdgeWithLemma(relationNode.lemma)
        s1ForRelation = 0
        for edge in edgeList:
            entityNode = None
            nodeA = edge.nodeA
            nodeB = edge.nodeB
            if nodeA.type == 'entity':
                entityNode = nodeA
            elif nodeB.type == "entity":
                entityNode = nodeB
            edgeList2,sumForRelation = self.getE_A_EdgeWithLemma(entityNode.lemma)
            s1ForRelation += entityNode.score * (edge.weight/sumForRelation)
        # NewRelationNode = copy.deepcopy(relationNode)
        # NewRelationNode.score = s1ForRelation
        return s1ForRelation

    def getE_E_EdgeWithLemma(self,lemma):
        edgeList = []
        sum = 0
        for edge in self.Graph:
            if (edge.nodeA.lemma == lemma or edge.nodeB.lemma == lemma) and (edge.nodeA.type == edge.nodeB.type):
                edgeList.append(edge)
                sum += edge.weight
                # print(edge.nodeA.lemma, edge.nodeB.lemma, edge.weight)
        return edgeList,sum

    def Hypothesis2ForEntity(self,entityNode,beta = 0.1):
        s2ForEntity = (1-beta) * entityNode.score
        edgeList,sumForEntityi = self.getE_E_EdgeWithLemma(entityNode.lemma)  # 根据ei找ej
        s2ForEntityItem2 = 0
        for edge in edgeList:
            entityJ = None
            nodeA = edge.nodeA
            nodeB = edge.nodeB
            if nodeA.lemma == entityNode.lemma:
                entityJ = nodeB
            elif nodeB.lemma == entityNode.lemma:
                entityJ = nodeA
            edgeListJ ,sumForEntityJ = self.getE_E_EdgeWithLemma(entityJ.lemma)  # 根据ej找en，并获得所有与ej相连的edge的权重之和
            s2ForEntityItem2 += entityJ.score*(edge.weight/sumForEntityJ)
        s2ForEntity += beta * s2ForEntityItem2
        # NewEntityNode = copy.deepcopy(entityNode)
        # NewEntityNode.score = s2ForEntity
        return s2ForEntity

    def Hypothesis2ForRelation(self,relationNode,beta = 0.1):
        s2ForRelation = (1-beta) * relationNode.score
        edgeList,sumForRelationi = self.getE_E_EdgeWithLemma(relationNode.lemma)  # 根据ai找aj
        s2ForRelationItem2 = 0
        for edge in edgeList:
            RelationJ = None
            nodeA = edge.nodeA
            nodeB = edge.nodeB
            if nodeA.lemma == relationNode.lemma:
                RelationJ = nodeB
            elif nodeB.lemma == relationNode.lemma:
                RelationJ = nodeA
            edgeListJ ,sumForRelationJ = self.getE_E_EdgeWithLemma(RelationJ.lemma)  # 根据aj找an，并获得所有与aj相连的edge的权重之和
            # print(relationNode.lemma,RelationJ.lemma,sumForRelationJ)
            s2ForRelationItem2 += RelationJ.score*(edge.weight/sumForRelationJ)
        s2ForRelation += beta * s2ForRelationItem2
        # NewEntityNode = copy.deepcopy(relationNode)
        # NewEntityNode.score = s2ForRelation
        return s2ForRelation

    def combine1and2(self,node,alpha = 0.2):
        if node.type == 'entity':
            s1ForEntity = self.Hypothesis1ForEntity(node)
            s2ForEntity = self.Hypothesis2ForEntity(node)

            # print(node.lemma,s1ForEntity,s2ForEntity)
            newScore = (1-alpha)*s1ForEntity + alpha*s2ForEntity
            newNode = copy.deepcopy(node)
            newNode.score = newScore
            return newNode
        elif node.type == 'relation':
            s1ForRelation = self.Hypothesis1ForRelation(node)
            s2ForRelation = self.Hypothesis2ForRelation(node)
            # print(node.lemma,s1ForRelation,s2ForRelation)
            newScore = (1-alpha)*s1ForRelation + alpha*s2ForRelation
            newNode = copy.deepcopy(node)
            newNode.score = newScore
            return newNode



    def getNodeInNodeList(self,lemma,newNodeList):
        """
        根据lemma获得节点
        :param lemma: 需要节点的lemma
        :param newNodeList: 需要查找的列表
        :return:
        """
        for node in newNodeList:
            if node.lemma == lemma:
                return node


    def outputAsGraphForList(self, Graph, seed, iter):
        rand = random()
        fontname = "FangSong"
        g = Digraph('a')
        # g.engine = 'twopi'
        for edge in Graph:
            if edge.nodeA.type == 'entity':
                 g.node(name=str(edge.nodeA.lemma) + "\n" + str(format(edge.nodeA.score, '.3f')),
                               fontname="FangSong")
            elif edge.nodeA.type == 'relation':
                 g.node(name=str(edge.nodeA.lemma) + "\n" + str(format(edge.nodeA.score, '.3f')),
                               fontname="FangSong", shape="box")
            if edge.nodeB.type == 'entity':
                 g.node(name=str(edge.nodeB.lemma) + "\n" + str(format(edge.nodeB.score, '.3f')),
                               fontname="FangSong")
            elif edge.nodeB.type == 'relation':
                 g.node(name=str(edge.nodeB.lemma) + "\n" + str(format(edge.nodeB.score, '.3f')),
                               fontname="FangSong", shape="box")
            # print(str(edge.nodeA.lemma))
            g.edge(tail_name=str(edge.nodeA.lemma) + "\n" + str(format(edge.nodeA.score, '.3f')),
                   head_name=str(edge.nodeB.lemma) + "\n" + str(format(edge.nodeB.score, '.3f')), fontname="FangSong",
                   label=str(edge.weight))
        g.render('result_file\\Model1Result\\hasEEANDRRGraph\\' + str(seed) + "_"+str(rand) + str(iter) + 'pair.gv', view=False)


    def getNumOfCo(self,verb1,verb2,maxDistance = 10):
        """
        两个关系在多少个句子中共现了
        :param verb1: 关系1
        :param verb2: 关系2
        :param maxDistance: 两者之间的最大距离不能超过 (default:10)
        :return:
        """
        sum = 0
        for key in self.sentenceDict:
            sentence = self.sentenceDict[key]
            # print(sentence)
            flag1 = False
            flag2 = False
            position1 = -100
            position2 = -100
            for item in sentence:
                word = item[0]
                location = word.find("_")
                numlocation = word.find("#")
                clean_word = word[numlocation + 1:location]
                # print(clean_word)
                if verb1 == clean_word:
                    # print(clean_word)
                    flag1 = True
                    position1 = item[1]
                elif verb2 == clean_word:
                    flag2 = True
                    position2 = item[1]

                if flag1==True and flag2==True :  # 当两个条件都满足时，输出
                    if position1 > position2:
                        if position1 - position2 - len(verb2) <=10:
                            sum+=1
                            break  # 当一个句子中存在一个满足这样的情况，就跳过，进行下一个句子
                    elif position1 < position2:
                        if position2 - position1 - len(verb1) <=10:
                            sum += 1
                            break
        # print(sum)
        return sum


    def getNumOfRECo(self,entity,verb,maxDistance = 10):
        """
        实体和关系共现次数，这里只考虑非种子实体与关系，所以该实体应该出现了关系的后面
        :param entity: 共现实体
        :param verb: 共现关系
        :param maxDistance: 两者之间的最大距离不能超过 (default:10)
        :return:
        """
        sum = 0
        for key in self.sentenceDict:
            sentence = self.sentenceDict[key]
            # print(sentence)
            flag1 = False
            flag2 = False
            position1 = -100
            position2 = -100
            itemPos1 = -100
            itemPos2 = -100
            count = -1
            for item in sentence:
                count +=1
                word = item[0]
                location = word.find("_")
                numlocation = word.find("#")
                clean_word = word[numlocation + 1:location]
                # print(clean_word)
                if entity == clean_word:
                    # print(clean_word)
                    flag1 = True
                    position1 = item[1]  # 实体位置
                    itemPos1 = count
                elif verb == clean_word:
                    flag2 = True
                    position2 = item[1]  # 关系位置
                    itemPos2 = count

                if flag1==True and flag2==True :  # 当两个条件都满足时，输出
                    # 实体只能出现在关系的后面
                    rel_entity_has_entity = False
                    if position1 > position2:
                        for index in range(itemPos2+1,itemPos1):
                            # print(index)
                            aaEntity = sentence[index]
                            if '#' in aaEntity[0]:
                                rel_entity_has_entity = True
                        if position1 - position2 - len(verb) <=10 and rel_entity_has_entity == False:
                            sum+=1
                            break  # 当一个句子中存在一个满足这样的情况，就跳过，进行下一个句子
        # print(sum)
        return sum


    def addEdgeBetweenR_R(self,nodeList):
        """
        将关系和关系之间的边，加入到Graph中
        :param nodeList: Graph所有节点列表
        :return:
        """
        relationNodeList = []  # 获取所有关系节点
        for node in nodeList:
            if node.type == 'relation':
                relationNodeList.append(node)
        for i in range(len(relationNodeList)):
            hNode = relationNodeList[i]  # 头关系节点
            for j in range(i + 1, len(relationNodeList)):
                tNode = relationNodeList[j]  # 尾关系节点
                if (hNode.lemma,tNode.lemma) in self.v_v_Co_Dict:
                    weight = self.v_v_Co_Dict[(hNode.lemma,tNode.lemma)]
                elif (tNode.lemma,hNode.lemma) in self.v_v_Co_Dict:
                    weight = self.v_v_Co_Dict[(tNode.lemma,hNode.lemma)]
                else:
                    weight = self.similarity(hNode.lemma,tNode.lemma)
                    self.v_v_Co_Dict[(hNode.lemma, tNode.lemma)] = weight
                    # if hNode.lemma in self.wv_from_text and tNode.lemma in self.wv_from_text:
                    #     weight = self.wv_from_text.similarity(hNode.lemma,tNode.lemma)
                    #     # weight = self.getNumOfCo(hNode.lemma,tNode.lemma)  # 获得头尾关系共现的次数
                    #     self.v_v_Co_Dict[(hNode.lemma,tNode.lemma)] = weight
                    # else:
                    #     weight = 0
                # print(hNode.lemma,tNode.lemma,weight)
                if weight > 0.7 :
                    edge = Edge(hNode,tNode,weight)  # 如果共现次数>0，把边加到Graph中
                    # print("Here!!!Be care!!!")
                    self.Graph.append(edge)
                    self.hasRREdge = True

    def addEdgeBetweenE_E(self,nodeList):
        """
        将关系和关系之间的边，加入到Graph中
        :param nodeList: Graph所有节点列表
        :return:
        """
        entityNodeList = []  # 获取所有实体节点
        for node in nodeList:
            if node.type == 'entity':
                entityNodeList.append(node)
        for i in range(len(entityNodeList)):
            hNode = entityNodeList[i]  # 头实体节点
            for j in range(i + 1, len(entityNodeList)):
                tNode = entityNodeList[j]  # 尾实体节点
                if (hNode.lemma,tNode.lemma) in self.v_v_Co_Dict:
                    weight = self.v_v_Co_Dict[(hNode.lemma,tNode.lemma)]
                elif (tNode.lemma,hNode.lemma) in self.v_v_Co_Dict:
                    weight = self.v_v_Co_Dict[(tNode.lemma,hNode.lemma)]
                else:
                    weight = self.similarity(hNode.lemma, tNode.lemma)
                    self.v_v_Co_Dict[(hNode.lemma, tNode.lemma)] = weight
                    # if hNode.lemma in self.wv_from_text and tNode.lemma in self.wv_from_text:
                    #     weight = self.wv_from_text.similarity(hNode.lemma, tNode.lemma)
                    #     # weight = self.getNumOfCo(hNode.lemma,tNode.lemma)  # 获得头尾关系共现的次数
                    #     self.v_v_Co_Dict[(hNode.lemma, tNode.lemma)] = weight
                    # else:
                    #     weight = 0
                # weight = self.getNumOfCo(hNode.lemma,tNode.lemma)  # 获得头尾实体共现的次数
                # print(hNode.lemma,tNode.lemma,weight)
                if weight > 0.7 :
                    # print(hNode.lemma,tNode.lemma,weight)
                    edge = Edge(hNode,tNode,weight)  # 如果共现次数>0，且该边不存在与Graph中，把边加到Graph中
                    if self.graphHasEdge(self.Graph,edge) == False:
                        # print("Here!!!Be care!!!")
                        self.Graph.append(edge)
                        self.hasEEEdge = True

    def addEdgeBetweenE_R(self,nodeList):
        """
        将与种子实体共现的实体和与种子实体共现的关系连接起来
        :param nodeList: Graph所有节点列表
        :return:
        """
        entityNodeList = []  # 获取所有实体节点
        for node in nodeList:
            if node.type == 'entity':
                entityNodeList.append(node)
        relationNodeList = []  # 获取所有实体节点
        for node in nodeList:
            if node.type == 'relation':
                relationNodeList.append(node)
        for i in range(len(entityNodeList)):
            eNode = entityNodeList[i]  # 实体节点
            for j in range(len(relationNodeList)):
                rNode = relationNodeList[j]  # 关系节点
                weight = self.getNumOfRECo(eNode.lemma,rNode.lemma)  # 获得实体、关系共现的次数
                # print(hNode.lemma,tNode.lemma,weight)
                if weight > 0 :
                    edge = Edge(eNode,rNode,weight)  # 如果共现次数>0，且该边不存在与Graph中，把边加到Graph中
                    if self.graphHasEdge(self.Graph,edge) == False:
                        # print("Here!!!Be care!!!")
                        self.Graph.append(edge)

    def main(self,seed,seedType):
        """
        主函数
        :param seed: 种子实体
        :param seedType: 尾实体的类型
        :return:
        """
        entityList, relationList = self.getEntityAndRelationBySeeds(seed, seedType, True, 'entity', True,
                                                               True)  # 获得与种子实体相连的实体和关系
        # for entity in entityList:
        #     self.getEntityAndRelationBySeeds(entity, seedType, False, 'entity', False, True)  # 获得与由上一步生成的实体相连的关系



        # for relation in relationList:
        # getEntityAndRelationBySeeds(relation,'PER','relation',False,True)
        # print(self.Graph)
        nodeList = self.nodeDict.values()
        self.addEdgeBetweenE_R(nodeList)  # 加入实体-关系边
        self.addEdgeBetweenE_E(nodeList)  # 加入实体-实体边。
        self.addEdgeBetweenR_R(nodeList)  # 加入关系-关系边。
        # for edge in self.Graph:
        #     print(edge.nodeA.lemma, edge.nodeB.lemma, edge.weight)

        # self.outputAsGraphForList(self.Graph, seed, -2 * 20)
        max_iter = 20  # 最大迭代次数

        aveModifyVal = []  # 记录每个节点修改值的平均值
        for i in range(max_iter):
            newNodeList = []  # 初始化每一次迭代新的节点列表
            modifyVal = []  # 每个节点修改的值
            for node in nodeList:  # 遍历每个节点
                newNode = self.combine1and2(node)  # 得到一个新的节点，newNode与node的区别就是score不一样
                newNodeList.append(newNode)
                modifyVal.append(abs(newNode.score - node.score))
            aveModifyVal.append(sum(modifyVal) / len(modifyVal))
            for edge in self.Graph:  # 遍历每条边
                edge.nodeA = self.getNodeInNodeList(edge.nodeA.lemma, newNodeList)  # 将每条边的节点用新生成的节点列表中的节点代替
                edge.nodeB = self.getNodeInNodeList(edge.nodeB.lemma, newNodeList)

                # print(edge.nodeA.lemma,edge.nodeA.score,edge.nodeB.lemma,edge.nodeB.score,)
            # print('--------------------------------------')
            nodeList = newNodeList  # 进行下一次迭代
            # self.outputAsGraphForList(self.Graph, seed, i)
        relationDict = dict()

        entityDict = dict()
        for node in nodeList:
            if node.type == 'relation':
                relationDict[node.lemma] = node.score
            elif node.type == 'entity':
                entityDict[node.lemma] = node.score

        # print(relationDict.keys())
        # print(entityDict.keys())
        entityDict = sorted(entityDict.items(), key=lambda item: item[1], reverse=True)
        relationDict = sorted(relationDict.items(), key=lambda item: item[1], reverse=True)  # 给最终的关系节点根据score排序
        # print(entityDict)
        # print(relationDict)
        # print(aveModifyVal)
        # outputAsGraphForList()
        x = range(len(aveModifyVal))
        y = aveModifyVal
        self.Graph = []
        self.nodeDict = dict()

        # plot中参数的含义分别是横轴值，纵轴值，颜色，透明度和标签
        # plt.plot(x, aveModifyVal, 'ro-', color='#4169E1', alpha=0.8, label='一些数字')
        # plt.show()
        return entityDict,relationDict
    def start(self):
        loc_dict = dict()
        for entity in self.all_entity:
            entityDict, relationDict = self.main(entity, "ALL")
            newList = []
            newList.append(entityDict)
            newList.append(relationDict)
            loc_dict[entity] = newList
        # print(loc_dict)
        return loc_dict

    def getLocalIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def similarity(self,word1,word2):

        url = 'http://'+self.localIp+':'+str(self.port)+'/sim?word1='+word1+'&word2='+word2
        print(url)
        h = requests.get(url)
        result = eval(h.text)
        # print(type(triples))
        if isinstance(result, str):
            return 0
        else:
            # print(result.get('similarity'))
            return result.get('similarity')
OREMain.py
import gensim

from Graph_ConstructionV0_4_4_1 import GraphForEntityV0_4_4
from entity_verb_new_containP2 import entity_verb_new
from readFile import readRawFile
import json
import time

def generateTop(json_file):
    tripleList = []
    for key in json_file:
        allList = json_file[key]
        entityList = allList[0]
        relationList = allList[1]
        # print(entityList)
        # print(relationList)

        rIndex = 0
        if len(entityList) == 1 or len(relationList) == 0:
            continue
        newEntityList = []
        for entity in entityList:
            if entity[0] != key:
                newEntityList.append(entity)
        # print(newEntityList)
        while len(relationList)> rIndex and relationList[rIndex][1] == relationList[0][1]:
            rIndex += 1
            eIndex = 0
            while len(newEntityList)> eIndex and newEntityList[eIndex][1] == newEntityList[0][1]:

                triple = []
                triple.append(key)
                triple.append(relationList[rIndex - 1][0])
                triple.append(newEntityList[eIndex][0])
                # if triple[1][1] >= 0.1 and triple[2][1] >= 0.1:
                tripleList.append(triple)
                # else:
                #     print(triple)
                eIndex += 1

    return tripleList


def chooseSituation(sentenceDict, json_file):
    clean_triple1 = []
    clean_triple2 = []
    clean_triple3 = []
    for triple in json_file:
        headEntity = triple[0]
        rel = triple[1]
        tailEntity = triple[2]
        Situation1AlreadyGet = False
        for sentenceID in sentenceDict:

            if Situation1AlreadyGet == True:
                break
            flag1 = False
            flag2 = False
            flag3 = False
            headEntityPosition = -100
            relPosition = -100
            tailEntityPosition = -100
            headEntityIndex = -100
            relIndex = -100
            tailEntityIndex = -100
            sentence = sentenceDict[sentenceID]
            for item in sentence:
                word = item[0]
                location = word.find("_")
                Numlocation = word.find("#")
                clean_word = word[Numlocation + 1:location]  # 得到每个item的词语
                itemIndex = sentence.index(item)

                if clean_word == headEntity:  # 如果该词与headEntity一样
                    headEntityPosition = item[1]
                    headEntityIndex = itemIndex
                    flag1 =True
                if clean_word == rel:
                    relPosition = item[1]
                    relIndex = itemIndex
                    flag2 =True
                if clean_word == tailEntity:
                    tailEntityPosition = item[1]
                    tailEntityIndex = itemIndex
                    flag3 =True
                if flag1 == True and flag2 == True and flag3 == True and (headEntityPosition == item[1] or \
                    relPosition == item[1] or tailEntityPosition == item[1]  ):
                    if relPosition<= tailEntityPosition and tailEntityPosition - relPosition - len(rel) <=10 \
                            and relPosition >= headEntityPosition and relPosition - headEntityPosition - len(headEntity) <= 10 and \
                            tailEntityPosition >= headEntityPosition and \
                            (tailEntityPosition - headEntityPosition - len(headEntity)) <=10 :
                        Situation1AlreadyGet = True
                        clean_triple1.append(triple)
                        break
        if Situation1AlreadyGet == False:
            Situation2AlreadyGet = False
            for sentenceID in sentenceDict:
                if Situation2AlreadyGet == True:
                    break
                flag2 = False
                flag3 = False
                relPosition = -100
                tailEntityPosition = -100
                sentence = sentenceDict[sentenceID]
                for item in sentence:
                    word = item[0]
                    location = word.find("_")
                    Numlocation = word.find("#")
                    clean_word = word[Numlocation + 1:location]  # 得到每个item的词语
                    if clean_word == rel:
                        relPosition = item[1]
                        flag2 =True
                    if clean_word == tailEntity:
                        tailEntityPosition = item[1]
                        flag3 =True
                    if flag2 == True and flag3 == True and (\
                        relPosition == item[1] or tailEntityPosition == item[1] ):
                        if relPosition<= tailEntityPosition  and tailEntityPosition - relPosition - len(rel) <=10 :
                            Situation2AlreadyGet = True
                            clean_triple2.append(triple)
                            break
            if Situation2AlreadyGet == False:
                clean_triple3.append(triple)

    return clean_triple1,clean_triple2,clean_triple3
def main(text,localIp,port):
    startTime = time.time()
    print("开始加载....")
    # wv_from_text = gensim.models.KeyedVectors.load(
    #     r"D:\\腾讯语料\\Tencent_AILab_ChineseEmbedding\\ChineseEmbedding_allWords.bin", mmap='r')
    print('加载完成....')
    TecentTime = time.time()
    print("语料加载时间为" + str(TecentTime - startTime))

    entity_verb_new1 = entity_verb_new()
    all_entity, sentenceDict = entity_verb_new1.main(text)
    readRawFile1 = readRawFile()
    rawSentenceDict = readRawFile1.main(text)
    # print(sentenceDict)
    PreTime = time.time()
    print("预处理时间："+str(PreTime - TecentTime))
    print(sentenceDict)
    print(rawSentenceDict)
    g1 = GraphForEntityV0_4_4(sentenceDict, rawSentenceDict, all_entity,localIp,port)
    # g1 = GraphForEntityV0_4_4(sentenceDict, rawSentenceDict, all_entity, wv_from_text)
    result1 = g1.start()
    ProTime = time.time()
    print("抽取时间："+str(ProTime - PreTime))
    result2 = generateTop(result1)
    clean_triple1,clean_triple2,clean_triple3 = chooseSituation(sentenceDict,result2)
    # print(clean_triple1)
    # print(clean_triple2)
    # print(clean_triple3)
    PostProTime = time.time()
    print("后处理时间："+str(PostProTime - ProTime))
    print("总时间:"+str(PostProTime - startTime))
    return all_entity,clean_triple1
if __name__ == '__main__':
    text = "光绪二十四年（1898年）四月二十八日（6月16日），光绪帝在颐和园仁寿殿召见康有为，命康在总署章京上行走，并许其专折奏事。在变法期间（6月至9月间），慈禧一直住在颐和园。变法失败后，光绪被长期幽禁在园中的玉澜堂。===光绪二十六年（1900年）七月二十一日（8月15日），八国联军侵占北京。慈禧太后和光绪帝经颐和园出逃。七月二十五日（8月19日），俄国军队首先侵占颐和园。以后，日、英、意军又相继占据。===民国十六年（1927年）6月2日，中国近代著名学者王国维自沉于昆明湖，终年50岁 ===。"
    # print(len(text))
    main(text)
demo1.py
# -*- coding: utf-8 -*-
from flask_cors import cross_origin
import json

import gensim
from flask import Flask, request
from flask import jsonify
import argparse
import sys
import socket
import time

import logging
import OREMain
from LTPNLP.finalFile import allATT, noATT

app = Flask(__name__)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s;%(levelname)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)


def isNoneWords(word):
    if word is None or len(word)==0 or word not in model.vocab:
        return True
    else:
        return False

@app.route("/", methods=['GET'])
def welcome():

    vecAPI="http://"+localIp+":"+str(port)+"/vec?word=淘宝"
    simAPI="http://"+localIp+":"+str(port)+"/sim?word1=淘宝&word2=京东"
    topSimAPI="http://"+localIp+":"+str(port)+"/top_sim?word=淘宝"
    extractTriplesAPI = "http://"+localIp+":"+str(port)+"/ORE?text=光绪二十四年（1898年）四月二十八日（6月16日），光绪帝在颐和园仁寿殿召见康有为，命康在总署章京上行走，并许其专折奏事。在变法期间（6月至9月间），慈禧一直住在颐和园。变法失败后，光绪被长期幽禁在园中的玉澜堂。光绪二十六年（1900年）七月二十一日（8月15日），八国联军侵占北京。慈禧太后和光绪帝经颐和园出逃。七月二十五日（8月19日），俄国军队首先侵占颐和园。以后，日、英、意军又相继占据。民国十六年（1927年）6月2日，中国近代著名学者王国维自沉于昆明湖，终年50岁。"

    return "Welcome to word2vec api . <br/>\
    try this api below：<br/> \
    1. vec api:    <a href='"+vecAPI+"'>"+vecAPI+"</a> <br/>\
    2. sim api:    <a href='"+simAPI+"'>"+simAPI+"</a> <br/>\
    3. top sim api:    <a href='"+topSimAPI+"'>"+topSimAPI+"</a> <br/>\
    4. open relation extraction api:    <a href='"+extractTriplesAPI+"'>"+extractTriplesAPI+"</a> <br/>\
    "

@app.route("/vec", methods=['GET'])
def vec_route():
    word = request.args.get("word")
    if isNoneWords(word):
        return jsonify("word is null or not in model!")
    else:
        return jsonify({'word':word,'vector': model.word_vec(word).tolist()})

@app.route("/sim", methods=['GET','POST'])
def similarity_route():
    word1 = request.args.get("word1")
    word2 = request.args.get("word2")
    if isNoneWords(word1) or isNoneWords(word2):
        return jsonify("word is null or not in model!")
    else:
        return jsonify({'word1':word1,'word2':word2,'similarity':float(model.similarity(word1, word2))})

@app.route("/top_sim", methods=['GET'])
def top_similarity_route():
    word = request.args.get("word")
    if isNoneWords(word):
        return jsonify("word is null or not in model!")
    else:
        return jsonify({'word':word,'top_similar_words':model.similar_by_word(word, topn=20, restrict_vocab=None)})

def getLocalIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip=s.getsockname()[0]
    s.close()
    return ip

@app.route('/plus',methods = ['POST'])
def plus():
    data = json.loads(request.data.decode())
    x = data['x']
    y = data['y']
    return json.dumps(x+y)

@app.route('/ORE',methods = ['POST','GET'])
@cross_origin()
def ORE():
    text = request.args.get("text")
    # return "Hello world"
    # text = json.loads(request.value.get("text"))
    # data = json.loads(request.data.decode())
    # text = data['text']
    all_entity,tripleList1 = OREMain.main(text,localIp,port)
    print(tripleList1,all_entity)
    resulrDict = dict()
    startTime = time.time()
    all_entity,tripleList2 = allATT.main(all_entity,text)
    # print(tripleList2)
    endTime = time.time()
    print("DSNFs处理时间:" + str(endTime - startTime))

    # tripleListAll = tripleList1
    tripleListAll = tripleList1 + tripleList2
    print(list(set(tuple(t) for t in tripleListAll)))
    resulrDict['all_entity'] = all_entity
    resulrDict["allTripleList"] = list(set(tuple(t) for t in tripleListAll))
    resulrDict["GBTripleList"] = list(set(tuple(t) for t in tripleList1))
    resulrDict["DSNFsTripleList"] = list(set(tuple(t) for t in tripleList2))

    return jsonify(resulrDict)

def main():
    global model
    global port
    global localIp
    for arg in sys.argv[1:]:
        logger.debug(arg)

    host = '0.0.0.0'
    port = 8888
    localIp = getLocalIP()
    logger.debug("start load model:" )
    startTime = time.time()
    start_time = time.time()
    # 加载语料的txt文件
    model = gensim.models.KeyedVectors.load_word2vec_format( 'D:\\腾讯语料\\Tencent_AILab_ChineseEmbedding\\Tencent_AILab_ChineseEmbedding.txt',
                                                                       binary=False)

    # 加载预料的bin文件
    # model = gensim.models.KeyedVectors.load(
    #     r"D:\\腾讯语料\\Tencent_AILab_ChineseEmbedding\\ChineseEmbedding_allWords.bin", mmap='r')
    logger.debug("end load model:")
    endTime = time.time()
    print(endTime - start_time)
    # app.run(host=host, port=port,debug=True)
    app.run(host=host, port=port,threaded = True)

if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=8888,threaded = True)
    main()

"""
Created on Tue Dec 24 11:34:51 2019

@author: thinkpad
修改内容：用LTP对单个词进行词性标注
再用LTP对整句话先分词，再进行词性标注，不再去除停用词
加入时间名词，加入额外补充实体，考虑使用jieba分词，不考虑去除停用词
修改内容
与V0.2相似（先存储XLORE和LTP识别出来的实体），并整合V0.5的内容

没有LTP识别出来的实体
"""
import copy
import json
import re

import requests
import os
import jieba
from pyltp import Segmentor,SentenceSplitter,Postagger,NamedEntityRecognizer,Parser


class entity_verb_new:

    def __init__(self):
        default_model_dir = '..\\ltp_data_v3.4.0'  # LTP模型文件目录

        # default_model_dir = 'C:\\Users\\sun\\PycharmProjects\\SUNCode\\ltp_data_v3.4.0\\'  # LTP模型文件目录
        self.postagger = Postagger()
        postag_flag = self.postagger.load(os.path.join(default_model_dir, 'pos.model'))
        # 命名实体识别模型
        self.recognizer = NamedEntityRecognizer()
        ner_flag = self.recognizer.load(os.path.join(default_model_dir, 'ner.model'))

        self.jiebaI = jieba.Tokenizer()
        # print(self.all_entity)

    def not_empty(self,s):
        return s and "".join(s.split())

    def close(self):
        self.postagger.release()

    def splitSentence(self,text):
        pattern = r'。|！|？|；|=|,|，|、'
        result_list = re.split(pattern, text)
        result_list = list(filter(self.not_empty, result_list))
        #    print(result_list)
        return result_list

    def tempNoun(self,sentence_list):
        newTempNounByRe = []
        for rawSentence in sentence_list:
            tempNounByRe = []
            rawSentence = rawSentence.strip()
            rawSentence = rawSentence.replace(' ', '')
            pattern1 = re.compile(r"\d{1,4}年\d{1,2}月\d{1,2}日")
            pattern2 = re.compile(r"\d{1,4}年\d{1,2}月")
            pattern3 = re.compile(r"\d{1,2}月\d{1,2}日")
            pattern4 = re.compile(
                r"(((公元){0,1})(\d{1,4}年)((（((清朝)|(金朝)|(明朝)|(明代)|(明)|(清)){0,1})((贞元)|(崇德)|(顺治)|(康熙)|(雍正)|(乾隆)|(嘉庆)|(道光)|(咸丰)|(同治)|(光绪)|(宣统)|(洪武)|(建文)|(永乐)|(洪熙)|(宣德)|(正统)|(天顺)|(景泰)|(成化)|(弘治)|(正德)|(嘉靖)|(隆庆)|(万历)|(泰昌)|(天启)|(崇祯)|(民国))?([元初一二三四五六七八九十]*)年）)?)")
            pattern5 = re.compile(r"((公元)?(\d{1,4})(-|—|～){1}(\d{1,4})年)")
            pattern6 = re.compile(
                r"(((((清朝)|(金朝)|(元朝)|(明朝)|(清代)|(明代)|(金代)|(元代)|(南宋)|(北宋)|(元)|(金)|(明)|(清)|(东汉)|(北魏)|(唐)|(后晋)|()){0,1})((天福)|(显德)|(咸通)|(会昌)|(乾封)|(武德)|(元嘉)|(正始)|(阳嘉)|(清宁)|(周康王)|(元定宗)|(中统)|(至元)|(元贞)|(大德)|(至大)|(皇庆)|(延祐)|(至治)|(泰定)|(致和)|(天顺)|(天历)|(至顺)|(元统)|(至元)|(至正)|(收国)|(天辅)|(天会)|(天眷)|(皇统)|(贞元)|(天德)|(正隆)|(大定)|(兴庆)|(明昌)|(承安)|(泰和)|(天定)|(大安)|(崇庆)|(至宁)|(贞祐)|(兴定)|(元光)|(正大)|(开兴)|(天兴)|(建炎)|(绍兴)|(隆兴)|(乾道)|(绍熙)|(淳熙)|(庆元)|(嘉泰)|(开禧)|(嘉定)|(宝庆)|(绍定)|(端平)|(嘉熙)|(淳祐)|(宝祐)|(开庆)|(景定)|(咸淳)|(德祐)|(景炎)|(祥兴)|(建隆)|(乾德)|(开宝)|(太平兴国)|(雍熙)|(淳化)|(端拱)|(至道)|(咸平)|(贞元)|(崇德)|(顺治)|(康熙)|(雍正)|(乾隆)|(嘉庆)|(道光)|(咸丰)|(同治)|(光绪)|(宣统)|(洪武)|(建文)|(永乐)|(洪熙)|(宣德)|(正统)|(天顺)|(景泰)|(成化)|(弘治)|(正德)|(嘉靖)|(隆庆)|(万历)|(泰昌)|(天启)|(崇祯)|(民国)|(中华民国))([元初一二三四五六七八九十]*)(年[代间]{0,1})((（?(公元)?\d{4}年?）?)?))?([一|二|三|四|五|六|七|八|九|十|正]{1,2}月[初|一|二|三|四|五|六|七|八|九|十]{1,3}日?)?([一|二|三|四|五|六|七|八|九|十|正]{1,2}月)?([初|一|二|三|四|五|六|七|八|九|十]{1,3}日)?(（(\d{1,4}年)?(\d{1,2}月)?\d{1,2}日）)?((\d{1,4}年)?(\d{1,2}月)?\d{1,2}日)?)")

            pattern7 = re.compile(
                r"[一|二|三|四|五|六|七|八|九|十|正]{1,2}月[初|一|二|三|四|五|六|七|八|九|十]{1,3}日")

            result1 = pattern1.findall(rawSentence)
            result2 = pattern2.findall(rawSentence)
            result3 = pattern3.findall(rawSentence)
            result4 = pattern4.findall(rawSentence)
            result5 = pattern5.findall(rawSentence)
            result6 = pattern6.findall(rawSentence)
            result7 = pattern7.findall(rawSentence)
            # result8 = pattern8.findall(rawSentence)
            if len(result1) != 0:
                for result1_ in result1:
                    tempNounByRe.append(result1_)
            if len(result2) != 0:
                for result2_ in result2:
                    tempNounByRe.append(result2_)
            if len(result3) != 0:
                for result3_ in result3:
                    tempNounByRe.append(result3_)

            if len(result4) != 0:
                for result4_ in result4:
                    tempNounByRe.append(result4_[0])
            if len(result5) != 0:
                for result5_ in result5:
                    tempNounByRe.append(result5_[0])
            if len(result6) != 0:
                newResult6 = []
                for result6_ in result6:
                    if len(result6_[0]) != 0:
                        tempNounByRe.append(result6_[0])
                        newResult6.append(result6_[0])

            if len(result7) != 0:
                for result7_ in result7:
                    tempNounByRe.append(result7_)

            # newTempNounByRe = []
            if len(tempNounByRe) != 0:
                for noun in tempNounByRe:
                    if ('年' in noun or '月' in noun or '日' in noun) and len(noun) != 1:
                        newTempNounByRe.append(noun)

        newTempNounByRe = list(set(newTempNounByRe))
        # print(newTempNounByRe)
        return newTempNounByRe

    def netag(self, sentenceList):
        newWordList2 = []
        newPosList2 = []
        for sentence in sentenceList:
            lemmas = self.jiebaI.lcut(sentence)
            postags = self.postagger.postag(lemmas)
            # 命名实体识别
            netags = self.recognizer.recognize(lemmas, postags)
            # print('\t'.join(netags))
            newWordList = []
            newPosTagList = []
            location = 0
            namedEntityLemma = ''
            for i in range(len(netags)):
                netag = netags[i]
                postag = postags[i]
                word = lemmas[i]
                if netag == 'O':
                    newWordList.append(word)
                    newPosTagList.append(postag)
                if 'S' in netag:
                    newWordList.append(word)
                    self.all_entity.append(word)
                    if 'Ns' in netag:
                        newPosTagList.append('ns')
                    if 'Nh' in netag:
                        newPosTagList.append('nh')
                    if 'Ni' in netag:
                        newPosTagList.append('ni')

                if 'B' in netag:
                    namedEntityLemma = word
                if 'I' in netag:
                    namedEntityLemma += word
                if 'E' in netag:
                    namedEntityLemma += word
                    newWordList.append(namedEntityLemma)
                    self.all_entity.append(namedEntityLemma)
                    namedEntityLemma = ''
                    if 'Ns' in netag:
                        newPosTagList.append('ns')
                    if 'Nh' in netag:
                        newPosTagList.append('nh')
                    if 'Ni' in netag:
                        newPosTagList.append('ni')

            if namedEntityLemma != '':
                newWordList.append(namedEntityLemma)
                self.all_entity.append(namedEntityLemma)
                namedEntityLemma = ''
                if 'Ns' in netag:
                    newPosTagList.append('ns')
                if 'Nh' in netag:
                    newPosTagList.append('nh')
                if 'Ni' in netag:
                    newPosTagList.append('ni')
            newWordList2.append(newWordList)
            newPosList2.append(newPosTagList)
        return newWordList2,newPosList2


    def mapEntity(self,sentence_list,newWordList2,newPosList2):

        entity_in_all_sentence =[]
        for sentence,result_words,wordPosList in zip(sentence_list,newWordList2,newPosList2):
            flag = False
            entity_verb_dict = {}
            # result_words = self.jiebaI.lcut(sentence)
            # wordPosList = self.postagger.postag(result_words)
            result_pos = []
            for pos in wordPosList:
                result_pos.append(pos)
            # print(result_pos)
            # print(result_words)
            for entity in self.all_entity:
                if sentence.find(entity)!=-1:
                    flag = True
                    location = 0
                    index = 0
                    while location<len(sentence):
                        location = sentence.find(entity,location)
                        if location ==-1:
                            break
                        else:
                            index +=1
                            entity_verb_dict[str(index)+'#'+entity + '_' + 'entity'] = location
                            location+=len(entity)
                    # entity_in_each_sentence.append(entity+'_'+str(sentence.find(entity)))

            if flag:
                # splitWordList = self.splitWordOneSentence(sentence,thu1)
                count = 0
                for index in range(len(result_words)):
                    word = result_words[index]
                    pos = result_pos[index]
                    if pos == 'v':  # 不去除停用词，只要是动词即可
                        if index + 1 < len(result_words):
                            word_next = result_words[index + 1]
                            pos_next = result_pos[index + 1]
                            if pos_next == 'p':
                                entity_verb_dict[word+""+word_next+'_v_'+str(count)] = count  # 由于一句话中可能会出现多次，所以我们使用count来表明，该动词所在的位置。
                            else:
                                entity_verb_dict[word + '_v_' + str(count)] = count
                        else:
                            entity_verb_dict[word + '_v_' + str(count)] = count
                        # 而且一个动词也可能在一句话中出现多次，所以我们给动词+count，使动词唯一。
                    count += len(word)
            entity_verb_dict = sorted(entity_verb_dict.items(), key=lambda item: item[1])

            entity_in_all_sentence.append(entity_verb_dict)
        return entity_in_all_sentence

    def xlink(self,text):
        url = "http://166.111.68.66:8880/EntityLinkingWeb/linkingSubmit.action"
        lang = "zh"
        data = {"text": text, "lang": lang}

        request_result = requests.post(url, data)
        link_result = json.loads(request_result.text)
        results = []
        # print(link_result['ResultList'])
        for i in link_result['ResultList']:
            results.append(i['label'])
        return results

    def postProcess(self,json_file):
        newEVList = []
        for EVList in json_file:
            # print(EVList)
            EVListHelp = EVList[:]  # 建立一个help列表，帮助循环
            for item in EVListHelp:
                if item not in EVList:  # 若EVListHelp中的该项不存在EVList中（即，该项已删除，则不进行下列操作）
                    continue
                # print(item)
                word = item[0]
                position = item[1]
                if '#' in word:  # 如果该单词是一个实体
                    location = word.find("_")
                    Numlocation = word.find("#")
                    clean_word = word[Numlocation + 1:location]
                    # print("----------------out Loop------------------")
                    # print(clean_word)
                    leftRange = position
                    rightRange = position + len(clean_word) - 1
                    # print(leftRange, rightRange)
                    for otherItem in EVListHelp:
                        if otherItem not in EVList:  # 若EVListHelp中的该项不存在EVList中（即，该项已删除，则不进行下列操作），以防删除的元素不在EVList里
                            continue
                        otherWord = otherItem[0]
                        otherPosition = otherItem[1]
                        if '#' in otherWord:  # 如果该单词是一个实体
                            location = otherWord.find("_")
                            Numlocation = otherWord.find("#")
                            clean_word = otherWord[Numlocation + 1:location]

                            otherLeftRange = otherPosition
                            otherRightRange = otherPosition + len(clean_word) - 1
                            if otherLeftRange == leftRange and otherRightRange == rightRange:
                                continue
                            elif otherLeftRange >= leftRange and otherRightRange <= rightRange:
                                # print("---------Entity Inner Loop-----------------")
                                # print(clean_word)
                                # print(otherLeftRange, otherRightRange)
                                EVList.remove(otherItem)  # 对EVList里的该元素进行删除
                            elif otherRightRange > rightRange and otherLeftRange <= rightRange and item in EVList:
                                EVList.remove(item)
                            elif otherLeftRange < leftRange and otherRightRange >= leftRange and item in EVList:
                                EVList.remove(item)
                            else:
                                continue
                        elif 'v' in otherWord and '#' not in otherWord:  # 如果该单词不是一个实体，而且是一个动词
                            location = otherWord.find("_")
                            Numlocation = otherWord.find("#")
                            clean_word = otherWord[Numlocation + 1:location]

                            otherLeftRange = otherPosition
                            otherRightRange = otherPosition + len(clean_word) - 1
                            if otherLeftRange == leftRange and otherRightRange == rightRange and item in EVList:
                                EVList.remove(item)

                            elif otherLeftRange >= leftRange and otherRightRange <= rightRange:
                                # print("---------Verb Inner Loop-----------------")
                                # print(clean_word)
                                # print(otherLeftRange, otherRightRange)
                                EVList.remove(otherItem)  # 对EVList里的该元素进行删除
                            elif otherRightRange > rightRange and otherLeftRange <= rightRange and item in EVList:
                                EVList.remove(item)
                            elif otherLeftRange < leftRange and otherRightRange >= leftRange and item in EVList:
                                EVList.remove(item)
                            else:
                                continue
            # print(EVList)
            newEVList.append(EVList)

        i = -1
        line_dict = dict()
        for line in newEVList:
            i += 1
            # if len(line) != 0:
            line_dict[i] = line
        return line_dict



    def main(self,text):
        # print("123444")
        print(text)
        self.all_entity = self.xlink(text)
        print(self.all_entity)
        sentence_list = self.splitSentence(text)  # 将text分为句子列表
        noBlankSentenceList = []
        for sentence in sentence_list:
            sentence = sentence.replace(" ", "")
            sentence = sentence.replace("▪", "")
            sentence = sentence.replace('\xa0', "")
            sentence = sentence.replace('\u3000', "")
            noBlankSentenceList.append(sentence)
        self.tempNoun = self.tempNoun(noBlankSentenceList)
        self.all_entity = self.all_entity+self.tempNoun
        all_entity1 = copy.deepcopy(self.all_entity)
        for entity in all_entity1:
            if entity!=None:
                self.jiebaI.add_word(entity)
        newWordList2,newPosList2 = self.netag(noBlankSentenceList)
        all_entity2 = self.all_entity
        # print(set(all_entity2) - set(all_entity1))
        self.all_entity = list(set(self.all_entity))
        # print(self.all_entity)

        Entity_in_sentence = self.mapEntity(noBlankSentenceList, newWordList2,newPosList2 )
        # print(Entity_in_sentence)
        # print(Entity_in_sentence)
        self.close()
        dict = self.postProcess(Entity_in_sentence)
        return self.all_entity,dict

if __name__ == "__main__":
    entity_verb_new1 = entity_verb_new()
    line_dict = entity_verb_new1.main("光绪二十四年（1898年）四月二十八日（6月16日），光绪帝在颐和园仁寿殿召见康有为，命康在总署章京上行走，并许其专折奏事。在变法期间（6月至9月间），慈禧一直住在颐和园。变法失败后，光绪被长期幽禁在园中的玉澜堂。===光绪二十六年（1900年）七月二十一日（8月15日），八国联军侵占北京。慈禧太后和光绪帝经颐和园出逃。七月二十五日（8月19日），俄国军队首先侵占颐和园。以后，日、英、意军又相继占据。===民国十六年（1927年）6月2日，中国近代著名学者王国维自沉于昆明湖，终年50岁 ===。")
    # print(line_dict)
readFile.py
"""
首先，需要获得5篇文档的每个句子，并带有ID
"""
import json
import os
import re

class readRawFile():
    def __init__(self):
        pass

    def not_empty(self, s):
        return s and "".join(s.split())


    def splitSentence(self,text):
        pattern = r'。|！|？|；|=|,|，|、'
        result_list = re.split(pattern, text)
        result_list = list(filter(self.not_empty, result_list))
        #    print(result_list)
        return result_list

    def main(self,text):
        sentence_list = self.splitSentence(text)  # 将text分为句子列表
        # print(sentence_list)
        # i = -1
        line_dict = dict()
        i=-1
        for line in sentence_list:
            i += 1
            if len(line) != 0:
                line = line.replace('\xa0', "")
                line = line.replace('\u3000', "")
                line = line.replace('▪', "")
                # line = line.strip()
                line = line.replace(" ","")
                line_dict[i] = line
        return line_dict