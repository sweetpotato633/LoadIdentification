import os
import shutil
import hashlib


def get_file_path(root_path, file_list, dir_list):
    # 获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        # 获取目录或者文件的路径
        dir_file_path = os.path.join(root_path, dir_file)
        # 判断该路径为文件还是路径
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
            # 递归获取所有文件和目录的路径
            get_file_path(dir_file_path, file_list, dir_list)
        else:
            file_list.append(dir_file_path)


def execute_cmd(cmd_list, need_print=False):
    res_list = []
    for m_cmd in cmd_list:
        res = os.popen(m_cmd)
        if need_print:
            print(m_cmd)
        out_str = res.read()
        res_list.append(out_str)
    return res_list

def get_file_md5(file_path):
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        for line in f:
            m.update(line)
    md5code = m.hexdigest()
    return md5code


def get_file_size(file_path, mode='auto'):
    fsize = os.path.getsize(file_path)
    if mode.lower() == 'auto':
        fsize = fsize / float(1024 * 1024)
        if fsize < 1:
            fsize *= 1024
            size = "{n1:.2f}K".format(n1=fsize)
        else:
            size = "{n1:.2f}M".format(n1=fsize)

    elif mode.lower() == 'mb':
        fsize = fsize / float(1024 * 1024)
        size = "{n1:.2f}M".format(n1=fsize)
    elif mode.lower() == 'kb':
        fsize = fsize / float(1024)
        size = "{n1:.2f}K".format(n1=fsize)
    else:
        size = str(fsize)
    return size


def copyfile_with_dir(src_dir, des_dir):
    dir_list = des_dir.split(os.sep)
    if not os.path.exists(src_dir):
        print(src_dir + " 不存在，拷贝失败\n")
        return
    if len(dir_list) > 1:  # 是目录+文件的格式
        t_dir = os.sep.join(dir_list[:-1])  # 获取目录
        if not os.path.exists(t_dir):
            os.makedirs(t_dir)
    shutil.copyfile(src_dir, des_dir)
