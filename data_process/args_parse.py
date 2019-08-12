"""
this is a cmd interface
"""
import argparse
# from data_process import process as pc
import process as pc

# 创建一个解析器
parser = argparse.ArgumentParser()

# 添加参数
# positional arguments
parser.add_argument("filepath", help="input your csv file path")
parser.add_argument("tablepath", help="output table path")
parser.add_argument("imgpath", help="output image path")
# optional arguments
# 可选帧率标准，默认为25
parser.add_argument("--fps", type=int, help="choose fps standard")

# 开始解析
args = parser.parse_args()

# 应用解析出的参数
pc.data_analysis(file_path=args.filepath, output_filepath=args.tablepath,
                 output_imgpath=args.imgpath, chose_fps=args.fps)