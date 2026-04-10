# core/icon_manager.py

import os
import hashlib
import ctypes
from ctypes import wintypes
from PIL import Image, ImageTk
from core.paths import ICON_CACHE_DIR


def ensure_cache():
    os.makedirs(ICON_CACHE_DIR, exist_ok=True)


def get_icon_cache_path(exe_path: str) -> str:
    normalized = os.path.normcase(os.path.normpath(exe_path))
    digest = hashlib.md5(normalized.encode("utf-8")).hexdigest()
    return os.path.join(ICON_CACHE_DIR, f"{digest}.png")


def extract_icon(exe_path: str, output_path: str, size: int = 40) -> bool:
    """
    Extract the first icon from a Windows executable and save it as PNG.
    """
    if not os.path.exists(exe_path):
        return False

    try:
        shell32 = ctypes.windll.shell32
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        large = (wintypes.HICON * 1)()
        small = (wintypes.HICON * 1)()

        extracted_count = shell32.ExtractIconExW(exe_path, 0, large, small, 1)
        if extracted_count == 0:
            return False

        hicon = large[0] or small[0]
        if not hicon:
            return False

        class ICONINFO(ctypes.Structure):
            _fields_ = [
                ("fIcon", wintypes.BOOL),
                ("xHotspot", wintypes.DWORD),
                ("yHotspot", wintypes.DWORD),
                ("hbmMask", wintypes.HBITMAP),
                ("hbmColor", wintypes.HBITMAP),
            ]

        class BITMAP(ctypes.Structure):
            _fields_ = [
                ("bmType", wintypes.LONG),
                ("bmWidth", wintypes.LONG),
                ("bmHeight", wintypes.LONG),
                ("bmWidthBytes", wintypes.LONG),
                ("bmPlanes", ctypes.c_ushort),
                ("bmBitsPixel", ctypes.c_ushort),
                ("bmBits", ctypes.c_void_p),
            ]

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG),
                ("biPlanes", ctypes.c_ushort),
                ("biBitCount", ctypes.c_ushort),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]

        class BITMAPINFO(ctypes.Structure):
            _fields_ = [
                ("bmiHeader", BITMAPINFOHEADER),
                ("bmiColors", wintypes.DWORD * 3),
            ]

        icon_info = ICONINFO()
        if not user32.GetIconInfo(hicon, ctypes.byref(icon_info)):
            user32.DestroyIcon(hicon)
            return False

        bmp = BITMAP()
        hbm = icon_info.hbmColor or icon_info.hbmMask
        gdi32.GetObjectW(hbm, ctypes.sizeof(BITMAP), ctypes.byref(bmp))

        width = bmp.bmWidth
        height = bmp.bmHeight

        hdc = user32.GetDC(0)
        mem_dc = gdi32.CreateCompatibleDC(hdc)

        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = width
        bmi.bmiHeader.biHeight = -height
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0  # BI_RGB

        buffer_len = width * height * 4
        buffer = ctypes.create_string_buffer(buffer_len)

        result = gdi32.GetDIBits(
            mem_dc,
            hbm,
            0,
            height,
            buffer,
            ctypes.byref(bmi),
            0
        )

        success = False

        if result:
            image = Image.frombuffer(
                "RGBA",
                (width, height),
                buffer,
                "raw",
                "BGRA",
                0,
                1
            )
            image = image.resize((size, size), Image.LANCZOS)
            image.save(output_path, "PNG")
            success = True

        if icon_info.hbmColor:
            gdi32.DeleteObject(icon_info.hbmColor)
        if icon_info.hbmMask:
            gdi32.DeleteObject(icon_info.hbmMask)

        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(0, hdc)
        user32.DestroyIcon(hicon)

        return success

    except Exception:
        return False


def get_or_create_icon_image(exe_path: str, size: int = 40):
    """
    Return a Tkinter PhotoImage for a game executable.

    The function only accepts cache images that actually contain visible pixels.
    If a cached image is fully transparent or invalid, it is deleted and treated
    as missing so the launcher can fall back to the controller icon.
    """
    try:
        ensure_cache()

        cache_path = get_icon_cache_path(exe_path)

        if not os.path.exists(cache_path):
            success = extract_icon(exe_path, cache_path, size)
            if not success:
                return None

        image = Image.open(cache_path).convert("RGBA")

        # Reject fully transparent / visually empty images.
        if image.getbbox() is None:
            try:
                os.remove(cache_path)
            except OSError:
                pass
            return None

        image = image.resize((size, size), Image.LANCZOS)

        # Double-check again after resize, just to be safe.
        if image.getbbox() is None:
            try:
                os.remove(cache_path)
            except OSError:
                pass
            return None

        return ImageTk.PhotoImage(image)

    except Exception:
        return None