import re
from baike import getBaike


# 判断百度百科精准查找是否成功
def judge_direct_search_error(text):
    res = re.findall('<p class="sorryCont"><span class="sorryTxt">抱歉</span>，您所访问的页面不存在...</p>', text, re.S)
    return len(res) > 0


# 匹配精准查询内容
def direct_search_map(word):
    m = {}
    l = len(getBaike(word, no=[1,[]]).splitlines())
    for i in range(l):
        str = getBaike(word, no=[1,[i]])
        if i == 0:
            m['简介'] = str.splitlines()[1:]
        else:
            lines = str.splitlines()
            # m[lines[1]] = ''.join(f"{row}\n" for row in str.splitlines()[2:])
            m[lines[1][2:]] = lines[2:]
    return m


def mumble_search_map(word):
    res = []
    ans = getBaike(word, no=[1,[]])
    if len(ans) == 0:
        return None
    else:
        m = {}
        ans = getBaike(word, no=0).splitlines()[1:]
        index = 0
        count = 0
        while count < 2 and ans[index] != '':
            l = len(getBaike(word, no=[index+1,[]]).splitlines())
            for i in range(l):
                str = getBaike(word, no=[index+1, [i]])
                if i == 0:
                    m['简介'] = str.splitlines()[1:]
                else:
                    lines = str.splitlines()
                    m[lines[1][2:]] = lines[2:]
            count += 1
            index += 1
            res.append(m)
    return res


if __name__ == '__main__':
    print(mumble_search_map('a接线盒'))