from util import history_posts
import os
import glob

def save_posts():
    # 获取当前文件所在目录的上级目录
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # 拼接数据目录路径
    data_dir = os.path.join(current_dir, 'data')
    # 获取所有json文件路径
    filepaths = glob.glob(os.path.join(data_dir, '**/*.json'), recursive=True)
    for filepath in filepaths:
        data = history_posts(filepath)
        print("filepath: ", filepath, "articles: ", data["articles"])
        
save_posts()