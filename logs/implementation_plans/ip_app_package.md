# 将项目打包为可下载的独立桌面应用 (Desktop App)

我们完全可以通过 `PyInstaller` 将整个系统（Python 后端、前端界面、数据资产）打包成一个独立的 `.exe` 可执行文件。用户下载后无需配置任何 Python 环境，双击即可运行。

## 核心挑战与解决思路

在打包过程中，最主要的问题是**静态资源路径**和**动态代码加载**的处理。

1. **路径解析问题**：打包后，程序会被解压到一个临时目录（`sys._MEIPASS`），因此 `api_server.py` 中寻找 `frontend` 和 `data` 目录的方式需要根据是否被打包进行动态判断。
2. **动态模块加载问题**：`operator_repo.py` 使用了 `glob.glob` 扫描 `operators` 文件夹下的 `.py` 脚本并动态 `importlib`。PyInstaller 默认会将 Python 文件编译并塞入二进制包，导致 `glob` 找不到实体文件。
    * **解决方案**：我们将 `backend/function/logic/operators/` 以及 `data/` 目录作为 `datas` 强制打包进二进制文件，在运行时释放为真实的实体文件，以兼容现有的加载逻辑。

## Proposed Changes (需修改的文件)

### 1. `backend/utils/path_resolver.py` (新建)
编写一个统一的路径解析辅助函数，自动判断当前是否处于 PyInstaller 运行环境。
```python
import sys
import os

def get_base_path():
    """获取项目的真实根目录，兼容 PyInstaller 环境"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    # 假设在 backend/utils 下，往上回退两级到达根目录
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
```

### 2. `backend/main/api_server.py`
引入 `get_base_path()`，修改 `frontend_dir` 和 `avatars_dir` 的绝对路径定位方式，确保在打包后指向正确的临时目录。

### 3. `backend/main/operator_repo.py`
引入 `get_base_path()`，修改 `load_all` 的默认参数，确保指向 `get_base_path()` 下的相关目录。

### 4. `build_app.py` (新建构建脚本)
使用 PyInstaller API (或生成 `.spec` 文件) 执行打包。我们需要通过 `--add-data` 包含以下三个核心目录：
- `frontend/`
- `data/`
- `backend/function/logic/operators/`

同时使用 `--windowed` (或 `--noconsole`) 隐藏背后的黑框控制台。

## Verification Plan

1. 自动执行 `python build_app.py` 打包项目。
2. 运行打包好的 `dist/CupCalculation.exe`。
3. 测试程序是否能成功拉起 WebView 窗口。
4. 测试干员数据是否能正确加载（首页是否显示数据）。
5. 测试干员详情页、沙盒演练接口是否运作正常。

---

> [!IMPORTANT]
> **需要您的确认**：这个方案会生成一个独立的 `CupCalculation.exe`。如果您对打包方案没有异议，请点击 Proceed，我将开始为您改造代码并生成最终的 exe 文件！
