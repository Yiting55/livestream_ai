# emotion_analysis/__init__.py

# 导入分析功能模块和配置文件
from .emotion_analysis import analyze_emotion
from .emotion_config import EmotionConfig

# 可以提供更高级的封装或一些便捷的导出（例如合并的分析函数等）
__all__ = ["analyze_emotion", "EmotionConfig"]
