import os
import tempfile
from pathlib import Path
from typing import Tuple
import shutil
import streamlit as st

def save_upload_to_tempfile(uploaded_file, show_progress: bool = False) -> Tuple[str, str]:
    """
    将上传文件写入系统临时目录，返回 (文件路径, 目录路径)。
    """
    tmp_dir = tempfile.mkdtemp(prefix="live_")
    suffix = Path(uploaded_file.name).suffix
    tmp_path = os.path.join(tmp_dir, f"video{suffix}")

    data = uploaded_file.getbuffer()
    if show_progress:
        prog = st.progress(0, text="保存视频到临时目录…")
    else:
        prog = None

    chunk = 1 * 1024 * 1024  # 1MB
    total = len(data)
    with open(tmp_path, "wb") as f:
        for i in range(0, total, chunk):
            f.write(data[i:i+chunk])
            if prog:
                done = min(total, i + chunk)
                prog.progress(int(done / total * 100),
                              text=f"保存中… {done//(1024*1024)}/{total//(1024*1024)} MB")
    if prog:
        prog.empty()
    return tmp_path, tmp_dir

def remove_path(path: str) -> None:
    """删除文件或目录（静默失败）"""
    if not path:
        return
    try:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        elif os.path.isfile(path):
            os.remove(path)
    except Exception:
        pass
