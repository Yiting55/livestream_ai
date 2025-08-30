# scene_analysis/__init__.py
from .scene_config import SceneConfig
from .scene_analysis import analyze_video         # 输入本地视频路径
from .facade import analyze_scene_from_upload     # 输入上传文件(字节/文件对象)

__all__ = ["SceneConfig", "analyze_video", "analyze_scene_from_upload"]
__version__ = "0.2.0"  # 变更返回JSON结构时记得+1
