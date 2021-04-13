# -*- coding:UTF-8 -*-
import random
import string

id_base_str = "5984932C-A606-4B76-9738-CFEC5A61394B-00828"

# return a code with len:len
def rand_letter_digits(len):
    return ''.join(random.sample(string.ascii_uppercase + string.digits, len))


def rand_dig(len):
    return ''.join(random.sample(string.digits, len))

# return fake id list
def id_aug(raw_id_str, n):
    raw_id_list = raw_id_str.split('-')
    id_aug_res = []
    for i in range(0, n):
        id_aug_cur = []
        for j in range(0, len(raw_id_list)):
            if j == len(raw_id_list) - 1:
                id_aug_cur.append(rand_dig(len(raw_id_list[j])))
            else:
                id_aug_cur.append(rand_letter_digits(len(raw_id_list[j])))
        id_aug_res.append('-'.join(id_aug_cur))
    for item in id_aug_res:
        print(item)
    return id_aug_res


id_aug(id_base_str, 9)

