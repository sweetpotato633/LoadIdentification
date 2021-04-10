import time
import matplotlib.pyplot as plt
import numpy as np
import math
from ExpandLib.expand_file import get_file_path
import matplotlib as mpl


sample_per_wave = 128
average_window = 8
#vol_coeff = 356610720
vol_coeff = 178305360
#重新标定过 2021.4.9
cur_coeff = 596151

mpl.rcParams["font.sans-serif"]=["SimHei"]
mpl.rcParams["axes.unicode_minus"]=False

def read_file(file_path):
    with open(file_path, 'rb') as fp:
        start_time = time.time()
        content = fp.read()
        dec_list = [n for n in content[:]]
        time_used = time.time() - start_time
        msg = "加载文件 {file} 用时：{cost:.3f} 秒\n".format(file=file_path, cost=time_used)
        print(msg)
        return dec_list


def three_bytes_to_int(dec_list):
    if len(dec_list) != 3:
        return  0

    if dec_list[2] < 128:
        res = dec_list[2]*65536 + dec_list[1]*256 + dec_list[0]
    else:
        dec_list = [255-n for n in dec_list]
        res = dec_list[2] * 65536 + dec_list[1] * 256 + dec_list[0] + 1
        res = res * -1
    return res

def split_UI_data_single(dec_list):
    start_index = 0
    voltage_list = []
    current_list = []
    length_array = []
    for i in range(len(dec_list)):
        if (dec_list[i] == 104) and (dec_list[i + 1] == 49):
            start_index = i
            length_array.append(dec_list[i + 2])
            length_array.append(dec_list[i + 3])
            break
    length_per_frame = length_array[1] * 256 + length_array[0] + 2  # 计算帧长度 加上帧头帧尾
    msg = "每包数据长度为：{length} 字节\n".format(length=length_per_frame)
    print(msg)
    frame_count = (len(dec_list) - start_index) / length_per_frame
    msg = "共{count}帧数据\n".format(count=frame_count)
    print(msg)

    if int(frame_count * 1000) % 1000 != 0:
        print("有不完整帧，退出...\n")
        return
    start_time = time.time()
    print("开始生成电压电流波形数据\n")
    for i in range(int(frame_count)):
        temp_frame = dec_list[start_index + length_per_frame * i:start_index + length_per_frame * i + length_per_frame]
        temp_frame = temp_frame[5:]#去掉帧头帧尾
        for j in range(int(len(temp_frame)/6)):
            temp_list = temp_frame[j*6:j*6+3]
            voltage_list.append(three_bytes_to_int(temp_list))
            temp_list = temp_frame[j*6+3:j*6+6]
            current_list.append(three_bytes_to_int(temp_list))
    msg = "生成电压电流波形数据，用时：{t:.3f}秒\n".format(t=time.time() - start_time)
    print(msg)
    print("对数据进行校正...\n")
    vol_array = np.array(voltage_list,dtype='float64')
    cur_array = np.array(current_list,dtype='float64')
    vol_array = vol_array*vol_coeff/np.power(10,12)/1000
    cur_array = cur_array*cur_coeff/np.power(10,12)/1000
    start_time = time.time()
    msg = "数据校正完成，用时：{t:.3f}秒\n".format(t=time.time() - start_time)
    print(msg)
    vol_array = vol_array.reshape(vol_array.shape[0],1)
    cur_array = cur_array.reshape(cur_array.shape[0],1)
    #print(vol_array.shape,cur_array.shape)
    return vol_array,cur_array


def calc_power(vol,cur):
    start_time = time.time()
    print("开始计算：功率 RMS 谐波等参数")
    act_array = vol[:int(sample_per_wave/4)*(-1),:]*cur[:int(sample_per_wave/4)*(-1),:]
    react_array = vol[:int(sample_per_wave/4)*(-1),:]*cur[int(sample_per_wave/4):,:]


    #print(np.max(act_array))
    window_size = sample_per_wave*average_window

    l0 = int(act_array.shape[0]/window_size)
    act_array = act_array[:l0*window_size]
    react_array = react_array[:l0*window_size]
    i_rms_array = cur[:l0*window_size]

    act_array1 = act_array.reshape(-1,window_size)
    react_array1 = react_array.reshape(-1,window_size)
    i_rms_array = i_rms_array.reshape(-1,window_size)

    #FFT
    i_fft_array = np.abs(np.fft.fft(i_rms_array,axis=1))
    i_fft_array = np.fft.fftshift(i_fft_array,axes=(1,))
    #plt.figure()
    #xlabel = np.linspace(start=0, stop=3200, num=1280)
    #plt.plot(xlabel,i_fft_array[1000,:])

    #plt.show()
    amp_freq_array = i_fft_array[:,512::8]#抽取64次谐波分量
    for i in range(amp_freq_array.shape[0]):
        if amp_freq_array[i,1] < 5:
            amp_freq_array[i, :] = 0
        else:
            amp_freq_array[i,:] = amp_freq_array[i,:]/amp_freq_array[i,1]*100#计算谐波含量，相对于基波幅值

    #plt.figure()
    #plt.bar(x,amp_freq_array[1000,:])
    #plt.show()

    act_power = np.abs(np.sum(act_array1,axis=1)/window_size)
    act_power = act_power*100
    #react_power = np.abs(np.sum(react_array1,axis=1)/window_size)
    react_power = np.sum(react_array1, axis=1) / window_size
    react_power = react_power*100
    i_rms = np.sqrt(np.sum(i_rms_array**2,axis=1)/window_size)*100*2.97/4.3
    i_rms = i_rms*100
    msg = "数据计算完毕，用时 {cost:.3f} 秒\n".format(cost=time.time()-start_time)
    print(msg)
    return act_power,react_power,i_rms,amp_freq_array


def main_process():
    file_list = []
    dir_list = []
    get_file_path('Raw',file_list,dir_list)
    if len(file_list) == 0:
        print('无效数据，退出\n')
        return
    data_list = read_file(file_list[0])
    voltage,current = split_UI_data_single(data_list)
    act_power,react_power,i_rms,har_array = calc_power(voltage,current)
    offset = 0
    x_time = np.linspace(start=0,stop=act_power.shape[0]*0.2,num=act_power.shape[0])
    plt.figure()
    plt.plot(x_time,act_power[offset:],'b')
    plt.title(file_list[0])
    plt.xlabel('Second')
    plt.ylabel('W')

    #plt.figure()
    plt.plot(x_time,react_power[offset:],'r')
    #plt.title('reactive power')
    #plt.xlabel('Second')
    #plt.ylabel('Var')
    #plt.figure()
    plt.plot(x_time,i_rms[offset:],'g')
    #plt.title('Current RMS')
    #plt.xlabel('Second')
    #plt.ylabel('A')
    plt.legend(['active','reactive','current 0.01A'])

    plt.figure()
    plt.plot(x_time, har_array[offset:, 2], 'b--')
    plt.plot(x_time,har_array[offset:, 3], 'r')
    plt.plot(x_time,har_array[offset:, 4], 'c--')
    plt.plot(x_time,har_array[offset:, 5], 'b')
    plt.plot(x_time,har_array[offset:, 6], 'm--')
    plt.plot(x_time,har_array[offset:, 7], 'g')
    plt.plot(x_time,har_array[offset:, 8], 'g--')
    plt.plot(x_time,har_array[offset:, 9], 'y')
    plt.plot(x_time,har_array[offset:, 10], 'k--')
    plt.title('Harmonic')
    plt.xlabel('Seconds')
    plt.ylabel('谐波含量 %')
    plt.legend(['2次','3次','4次','5次','6次','7次','8次','9次','10次'])
    #plt.legend(['3次', '4次', '5次', '6次', '7次', '8次', '9次', '10次'])
    plt.show()


def test():
    t = np.linspace(start=0,stop=1,num=128*50)
    u_array = 220*np.sqrt(2)*np.sin(2*math.pi*50*t)
    i_array = 5*np.sqrt(2)*np.sin(2*math.pi*50*t)
    pow_array = u_array*i_array
    act_power = sum(pow_array)/pow_array.shape[0]
    u_rms = np.sum(u_array**2)/u_array.shape[0]
    u_rms = np.sqrt(u_rms)
    i_rms = np.sum(i_array**2)/i_array.shape[0]
    i_rms = np.sqrt(i_rms)
    print(act_power)
    plt.plot(i_array)
    plt.show()

if __name__ == "__main__":
    main_process()
    #test()
    print("finished\n")
