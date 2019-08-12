"""
1.数据导入
2.数据分析
3.绘图及制表
__author__: syyao
__version__: v1
__date__: 2019/07/04
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from pylab import mpl

# 解决中文显示问题
# 指定默认字体为 微软雅黑
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']
# 解决负号‘-’显示为方块的问题
mpl.rcParams['axes.unicode_minus'] = False


def import_csv(file_path):
    """
    导入CSV文件
    :param file_path: CSV文件的路径
    :return: 经过初步处理的dataframe
    """
    # 导入有列索引的CSV数据
    # 处理中文路径
    # with open(file_path) as f:
    #     df = pd.read_csv(f, header=0)
    df = pd.read_csv(u'%s' % file_path, header=0, index_col=False)

    # 获取列名
    # colName = df.columns
    # 为了防止以后更改列名，修改每一列的字段名为固定列名，以后若修改列名，直接改这里即可
    # df.columns = [""]

    # 提取 Mainlog=TRUE 的行记录
    df = df[df.Mainlog == True]

    # 求FPS的最大值
    if df.FPS.max() >= 59:
        # 去掉FPS<10的行记录
        df = df[df.FPS >= 10]
    elif df.FPS.max() <= 31:
        df = df[df.FPS >= 5]
    else:
        print("FPS_max在(30, 60)之间")
    return df


def data_process(df, chose_fps):
    """
    数据处理
    :param df: 经过初步处理的dataframe
    :param chose_fps: FPS标准值
    :return: 返回表格的内容
    """
    # 计算平均帧率avg_fps
    avg_fps = df.FPS.mean()
    # print(avg_fps)

    # 计算FPS小于等于25/35/55帧的占比
    num = df.FPS.count()
    fps_lt = df[df.FPS <= chose_fps].FPS.count() / num
    # print(fps_lt)

    # 计算帧率标准差fps_std
    fps_std = df.FPS.std(ddof=0)

    # 计算延时100ms以上每分钟次数
    delay_mt1 = df[['100~110ms', '110~120ms', '120ms~~~ms']].sum(axis=1).iloc[0]
    # print(delay_mt1)
    delay_mt2 = df[['100~110ms', '110~120ms', '120ms~~~ms']].sum(axis=1).iloc[-1]
    # print(delay_mt2)
    delay = (delay_mt2 - delay_mt1) / df['100~110ms'].count() * 60
    # print(delay)

    # 计算平均电流avg_curr
    avg_curr = df.AvgCurrent.mean()
    # print(avg_curr)

    # C1组大核运行过程中是否出现持续超过3秒的关闭状态（通过统计C1_count确认，如连续3个数值为0即为关闭）
    try:
        arr = list(df.C1_count)
        while True:
            first_index = arr.index(0)
            if arr[first_index+1] == 0 and arr[first_index+2] == 0:
                judgement = True
                break
            arr[first_index] = -1
    except:
        judgement = False

    # 计算CPU小核使用平均占比
    c0_cpumaxfreq = df.C0_cpumaxfreq.max()
    c0_cpufreq = df.C0_cpufreq.mean()
    avg_c0 = c0_cpufreq / c0_cpumaxfreq
    # print(avg_c0)

    # 计算CPU大核使用平均占比
    c1_cpumaxfreq = df.C1_cpumaxfreq.max()
    c1_cpufreq = df.C1_cpufreq.mean()
    avg_c1 = c1_cpufreq / c1_cpumaxfreq
    # print(avg_c1)

    # 计算GPU使用平均占比
    avg_gpu = df.GPU.mean()

    for_table = [avg_fps, fps_lt, fps_std, delay, avg_curr, judgement, avg_c0, avg_c1, avg_gpu, chose_fps]

    return for_table


def data_visualization(csv2df, for_table, output_filepath, output_imgpath):
    """
    数据可视化
    :param csv2df: 导入CSV文件得到的dataframe
    :param for_table: 经过数据处理和分析之后得到的表格数据
    :param output_filepath: 输出CSV文件的保存路径
    :param output_imgpath: 输出图片的保存路径
    :return: None
    """
    # 制表  'C1组大核运行过程中是否出现持续超过3秒的关闭状态（通过统计C1_Count确认，如数值为0即为关闭）',
    # 判断 要计算低于25/35/55帧的哪一种 的占比
    chose_fps = for_table[-1]
    # 列名称可以修改，但一定不要随意调整列名的顺序
    col_name = ['平均帧率', '低于%s帧' % chose_fps, '帧率标准差', '延时100ms以上每分钟次数',
                '平均电流', 'C1组大核运行过程中是否出现持续超过3秒的关闭状态', 'CPU小核使用平均占比', 'CPU大核使用平均占比', 'GPU使用平均值']

    # 生成一个dataframe
    for_table.pop()
    table_content = for_table
    df = dict()
    for i in range(len(col_name)):
        df[col_name[i]] = [table_content[i]]
    df = pd.DataFrame.from_dict(df)
    # print(df)

    # 将dataframe导出为csv文件，保留列字段名，去掉行索引
    # with open(output_filepath, 'w', encoding='gbk') as f:
    #     df.to_csv(f, index=False)
    df.to_csv(u'%s' % output_filepath, index=False, encoding="gbk")

    # 绘图
    df = csv2df

    # 绘制平均帧率曲线图
    num = df.FPS.count()
    x = [i for i in range(1, num + 1)]
    plt.figure(1)
    plt.subplot(3, 1, 1)
    # 控制坐标轴范围
    plt.axis([1, num, 0, int(df.FPS.max() + 10)])

    # x_interval 控制x轴坐标间隔
    x_int_fps = 50
    xtick_nums = num//x_int_fps+1
    plt.xticks([i * x_int_fps for i in range(xtick_nums)])

    # y_interval 控制y轴坐标间隔
    y_int_fps = 10
    ytick_nums = int(df.FPS.max() // y_int_fps) + 2
    plt.yticks([i * y_int_fps for i in range(ytick_nums)])

    plt.title("帧率统计图")
    plt.grid(color='lightgrey', axis='y')
    plt.plot(x, df.FPS, color='midnightblue')

    # 绘制c0曲线图
    plt.figure(1)
    plt.subplot(3, 1, 2)

    # 控制坐标轴范围
    plt.xlim(1, num)
    plt.ylim(0, int(df.C0_cpufreq.max()+500))

    x_int_c0 = 50
    xtick_nums = num//x_int_c0+1
    plt.xticks([i * x_int_c0 for i in range(xtick_nums)])

    # y_interval 控制y轴坐标间隔
    y_int_c0 = 500
    ytick_nums = int(df.C0_cpufreq.max() // 500) + 2
    plt.yticks([i * y_int_c0 for i in range(ytick_nums)])

    plt.title("C0频率统计图")
    plt.grid(color='lightgrey', axis='y')
    plt.plot(x, df.C0_cpufreq, color='midnightblue')

    # 绘制c1曲线图
    plt.figure(1)
    plt.subplot(3, 1, 3)

    # 控制坐标轴范围
    plt.xlim(1, num)
    plt.ylim(0, int(df.C1_cpufreq.max()+500))

    x_int_c1 = 50
    xtick_nums = num//x_int_c1+1
    plt.xticks([i * x_int_c1 for i in range(xtick_nums)])

    # y_interval 控制y轴坐标间隔
    y_int_c1 = 500
    ytick_nums = int(df.C1_cpufreq.max() // 500) + 2
    plt.yticks([i * y_int_c1 for i in range(ytick_nums)])

    plt.title("C1频率统计图")
    plt.grid(color='lightgrey', axis='y')
    plt.plot(x, df.C1_cpufreq, color='midnightblue')

    plt.subplots_adjust(wspace=0.25, hspace=0.5, bottom=0.13, top=0.9)
    plt.savefig(u'%s' % output_imgpath, dpi=400)
    plt.show()


def data_analysis(file_path, output_filepath, output_imgpath, chose_fps=25):
    """
    数据分析和绘图制表的最终接口函数
    :param file_path: CSV数据的路径
    :param output_filepath: 输出表格的路径
    :param output_imgpath: 输出图片的路径
    :param chose_fps: 可变帧率选择：25/35/55
    :return: None
    """
    csv2df = import_csv(file_path)
    for_table = data_process(csv2df, chose_fps)
    data_visualization(csv2df, for_table, output_filepath, output_imgpath)


if __name__ == "__main__":
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\frame11.csv"
    output_filepath = os.path.dirname(os.path.realpath(__file__)) + "\\report.csv"
    output_imgpath = os.path.dirname(os.path.realpath(__file__)) + "\\result.png"
    data_analysis(file_path, output_filepath, output_imgpath)