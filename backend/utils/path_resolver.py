import sys
import os

def get_base_path():
    """获取项目的真实根目录，兼容 PyInstaller 环境。"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # 当打包成 exe 后运行，会解压到 sys._MEIPASS，此时它就是根目录
        return sys._MEIPASS
    # 如果正常通过 Python 执行，往上回退两级到达根目录 (因为目前在 backend/utils)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
