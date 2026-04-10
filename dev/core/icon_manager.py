# core/icon_manager.py

import os
import hashlib
import ctypes
from PIL import Image, ImageTk
from core.paths import ICON_CACHE_DIR


def ensure_cache():
    os.makedirs(ICON_CACHE_DIR, exist_ok=True)


def get_icon_cache_path(exe_path: str) -> str:
    normalized = os.path.normcase(os.path.normpath(exe_path))
    digest = hashlib.md5(normalized.encode()).hexdigest()
    return os.path.join(ICON_CACHE_DIR, f"{digest}.png")


def extract_icon(exe_path, output_path, size=40):
    """
    Extract icon from exe using Windows API.
    """
    try:
        large, small = ctypes.windll.shell32.ExtractIconExW(exe_path, 0, None, None, 0)

        if large == 0:
            return False

        hicon = ctypes.windll.shell32.ExtractIconExW(exe_path, 0, None, None, 1)

        if not hicon:
            return False

        ico_x = ctypes.windll.user32.GetSystemMetrics(11)
        ico_y = ctypes.windll.user32.GetSystemMetrics(12)

        hdc = ctypes.windll.user32.GetDC(0)
        hbmp = ctypes.windll.gdi32.CreateCompatibleBitmap(hdc, ico_x, ico_y)
        hdc_mem = ctypes.windll.gdi32.CreateCompatibleDC(hdc)

        ctypes.windll.gdi32.SelectObject(hdc_mem, hbmp)
        ctypes.windll.user32.DrawIconEx(hdc_mem, 0, 0, hicon, ico_x, ico_y, 0, 0, 3)

        bmpinfo = ctypes.create_string_buffer(40)
        ctypes.windll.gdi32.GetObjectA(hbmp, 40, bmpinfo)

        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        image.save(output_path)

        return True

    except Exception:
        return False


def get_or_create_icon_image(exe_path: str, size=40):
    """
    Return PhotoImage for a game exe.
    """
    try:
        ensure_cache()

        cache_path = get_icon_cache_path(exe_path)

        if not os.path.exists(cache_path):
            success = extract_icon(exe_path, cache_path, size)

            if not success:
                return None

        image = Image.open(cache_path)
        image = image.resize((size, size))

        return ImageTk.PhotoImage(image)

    except Exception:
        return None