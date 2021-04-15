import jieba
from webSpider.src.utils import csvReader
import re
from ltp import LTP

# 括号处理
def quote_slice(a):
    result_list = re.findall(r"[(](.*?)[)]", a)
    for item in result_list:
        i = a.find(item)
        a = a[:i - 1] + a[i + len(item) + 1:]
    result_list.append(a)
    return result_list


# 任务文本分词_jieba
def work_detail_parser_jieba():
    f = csvReader("标准工作任务单")
    paList = []
    pbList = []
    for i, row in enumerate(f):
        if i != 0:
            val = row[1][5:].split('，')
            # print(val)
            pa = val[2]
            pb = val[3:]
            paList.append(jieba.lcut(pa, cut_all=False))
            for b in pb:
                pbList.append(jieba.lcut(b, cut_all=False))
    return paList, pbList


# 任务文本分词_ltp
def work_detail_parser_ltp():
    f = csvReader("标准工作任务单")
    ltp = LTP()
    paList = []
    pbList = []
    for i, row in enumerate(f):
        if i != 0:
            val = row[1][5:].split('，')
            paList.append(val[2])
            temp = val[3:]
            for v in temp:
                pbList.append(v)
    # print(paList)
    # print(pbList)
    sa, ha = ltp.seg(paList)
    sb, hb = ltp.seg(pbList)
    pa = ltp.pos(ha)
    pb = ltp.pos(hb)

    return sa, sb, pa, pb
    # for i in range(len(sa)):
    #     print(sa[i], pa[i])
    # for i in range(len(sb)):
    #     print(sb[i], pb[i])


# 任务概述分词_ltp
def work_summary_parser_ltp():
    f = csvReader("标准工作任务单")
    ltp = LTP()
    paList = []
    for i, row in enumerate(f):
        if i != 0:
            val = row[1][5:].split('，')
            paList.append(val[2])
    wa, ha = ltp.seg(paList)
    pa = ltp.pos(ha)
    return wa, pa


if __name__ == '__main__':
    sa, sb, pa, pb = work_detail_parser_ltp()

