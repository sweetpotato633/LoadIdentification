import ctypes
import numpy as np
import pandas as pd


def unsignedInt2Signed(num):
    num = int(num)
    res = ctypes.c_int16(num).value
    return res


def signedInt2Unsigned(num):
    num = int(num)
    res = ctypes.c_uint16(num).value
    return res


def int2Hex(num):
    num = int(num)
    if num < 0:
        num = signedInt2Unsigned(num)
    return hex(num)


def hexstr2Int2(hex_str, signed=False):
    t_str = ""
    if len(hex_str) > 4:
        t_str = hex_str[:-4]
    elif len(hex_str) < 4:
        t_len = 4 - len(hex_str)
        str_add = "0" * t_len
        t_str = str_add + hex_str
    else:
        t_str = hex_str
    b = bytes.fromhex(t_str)
    c = int.from_bytes(b, byteorder="big", signed=signed)
    return c


def hexstr2Int2_array(hex_frame, signed=False):
    row_count = len(hex_frame)
    column_count = len(list(hex_frame.columns))
    if signed:
        t_array = np.zeros((row_count,column_count),dtype='i2')
    else:
        t_array = np.zeros((row_count, column_count), dtype='u2')
    for i in range(row_count):
        for j in range(column_count):
            t_array[i,j] = hexstr2Int2(hex_frame.iloc[i,j],signed=signed)
    return t_array


def unsignedInt2Signed_array(data_array):
    t_array = np.asarray(data_array, dtype='i2')
    return t_array


def SignedInt2Unsigned_array(data_array):
    t_array = np.asarray(data_array, dtype='u2')
    return t_array


def Float2UnsignedInt_array(data_array):
    t_array = np.asarray(data_array, dtype='u2')
    return t_array


def Integer2ExcelIndex(num):
    alpha_range = ord('Z') - ord('A') + 1
    outer = int((num) / (alpha_range))
    inner = (num) % (alpha_range)
    if outer > 0:
        outer_str = chr(ord('A') + outer - 1)
    else:
        outer_str = ""
    inner_str = chr(ord('A') + inner)
    return outer_str + inner_str


if __name__ == "__main__":
    data = [["FFFF","AB"],["FFE","F"]]
    data_frame = pd.DataFrame(data)
    print(hexstr2Int2_array(data_frame,signed=True))
    input()
