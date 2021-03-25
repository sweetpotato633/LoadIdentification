import numpy as np


def ExpandArray(*expand_vector):
    if len(expand_vector) == 0:
        return None
    dim_array = len(expand_vector)
    length_list = 1
    while dim_array > 0:
        length_list *= len(expand_vector[dim_array-1])
        dim_array -= 1

    list_1 = np.array(expand_vector[len(expand_vector)-1])#先生成最后一维的列向量
    expand_len = int(length_list/len(list_1))
    list_1 = np.tile(list_1,expand_len)

    if len(expand_vector) == 1:#一维向量到这里直接返回就行了
        return list_1.T

    dim_array = len(expand_vector)-1
    unit_expand_len = len(expand_vector[len(expand_vector)-1])

    while dim_array > 0:#需要先进行元素复制，再进行向量复制
        vec_length = len(expand_vector[dim_array-1])#当前向量长度
        vec_expand_len = length_list/vec_length
        vec_expand_len /= unit_expand_len
        tlist = np.array(expand_vector[dim_array-1])
        tlist = np.repeat(tlist,int(unit_expand_len))#元素复制
        tlist = np.tile(tlist,int(vec_expand_len))#向量复制
        list_1 = np.vstack((list_1,tlist))
        dim_array -= 1
        unit_expand_len *= vec_length
    list_1 = list_1.T
    list_1 = np.fliplr(list_1)
    return list_1