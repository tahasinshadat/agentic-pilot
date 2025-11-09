import time
import winreg
import pyautogui
import ctypes
from ctypes import wintypes

# Default behavior
# Filter code mapping:
#   -1 disable (turn everything off, reset gamma)
#    0 grayscale           (Windows native)
#    1 inverted            (Windows native)
#    2 gray-inverted       (Windows native)
#    3 deuteranopia        (Windows native)
#    4 protanopia          (Windows native)
#    5 tritanopia          (Windows native)
#    6 warm                (gamma only: reduce blue light)
#    7 dim                 (gamma only: brightness down)
#    8 low_contrast        (gamma only)
#    9 high_contrast       (gamma only)
#   10 warm_dim            (gamma only)
#   11 warm_low_contrast   (gamma only)
DEFAULT_FILTER_TYPE = -1  # programmer can change this to any code above


REG_PATH = r"Software\Microsoft\ColorFiltering"

FILTER_PRESETS = {
    -1: {"kind": "disable"}, #default state
    0: {"kind": "win", "filter_type": 0, "name": "grayscale"}, #solves: visual overstimulation for ADHD
    1: {"kind": "win", "filter_type": 1, "name": "inverted"}, #solves: low vision
    2: {"kind": "win", "filter_type": 2, "name": "gray_inverted"}, #not useful
    3: {"kind": "win", "filter_type": 3, "name": "deuteranopia"}, #solves: deuteranopia
    4: {"kind": "win", "filter_type": 4, "name": "protanopia"}, #solves: protanopia
    5: {"kind": "win", "filter_type": 5, "name": "tritanopia"}, #solves: tritanopia
    6: {"kind": "gamma", "name": "warm", "warmth": 0.4}, #solves: blue light reduction for better sleep AKA night light
    7: {"kind": "gamma", "name": "dim", "brightness": 0.8}, #solves: eye strain in low light, epilepsy
    8: {"kind": "gamma", "name": "low_contrast", "contrast": 0.85}, #solves: visual stress for dyslexia
    9: {"kind": "gamma", "name": "high_contrast", "contrast": 1.15}, #solves: low vision
    10: {"kind": "gamma", "name": "warm_dim", "warmth": 0.4, "brightness": 0.85}, #solves: combined blue light reduction and dimming
    11: {"kind": "gamma", "name": "warm_low_contrast", "warmth": 0.4, "contrast": 0.9}, #solves: combined blue light reduction and low contrast
}


def _get_reg_dword(key, name, default=0):
    """Get a DWORD value from registry, return default if not found."""
    try:
        value, _ = winreg.QueryValueEx(key, name)
        return int(value)
    except FileNotFoundError:
        return default


def _set_reg_dword(key, name, value):
    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))


def toggle_filter_hotkey(delay=0.15):
    """Toggle filter via Win+Ctrl+C (respects system setting)."""
    time.sleep(delay)
    pyautogui.hotkey("win", "ctrl", "c")


# --- Gamma ramp based adjustments (blue light, brightness, contrast) ---

def _build_gamma_ramp(brightness=1.0, contrast=1.0, r_scale=1.0, g_scale=1.0, b_scale=1.0):
    brightness = max(0.0, min(1.5, float(brightness)))
    contrast = max(0.5, min(1.5, float(contrast)))
    r_scale = max(0.0, min(1.5, float(r_scale)))
    g_scale = max(0.0, min(1.5, float(g_scale)))
    b_scale = max(0.0, min(1.5, float(b_scale)))

    RampArray = (wintypes.WORD * 256) * 3
    ramp = RampArray()

    def clamp01(x):
        return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

    for i in range(256):
        x = i / 255.0
        y = (x - 0.5) * contrast + 0.5
        y *= brightness
        y = clamp01(y)

        r = clamp01(y * r_scale)
        g = clamp01(y * g_scale)
        b = clamp01(y * b_scale)

        ramp[0][i] = int(r * 65535)
        ramp[1][i] = int(g * 65535)
        ramp[2][i] = int(b * 65535)

    return ramp


def _set_gamma_ramp(ramp):
    gdi32 = ctypes.WinDLL("gdi32")
    user32 = ctypes.WinDLL("user32")
    user32.GetDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = (wintypes.HWND, wintypes.HDC)
    gdi32.SetDeviceGammaRamp.argtypes = (wintypes.HDC, ctypes.c_void_p)

    hdc = user32.GetDC(None)
    try:
        gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp))
    finally:
        user32.ReleaseDC(None, hdc)


def reset_gamma():
    RampArray = (wintypes.WORD * 256) * 3
    ramp = RampArray()
    for i in range(256):
        val = i * 256
        ramp[0][i] = val
        ramp[1][i] = val
        ramp[2][i] = val
    _set_gamma_ramp(ramp)


def _apply_gamma_preset(preset):
    wl = float(preset.get("warmth", 0.0))
    brightness = float(preset.get("brightness", 1.0))
    contrast = float(preset.get("contrast", 1.0))

    wl = max(0.0, min(1.0, wl))
    # approximate Windows Night light: reduce blue more than green
    r_scale = 1.0
    g_scale = 1.0 - (0.2 * wl)
    b_scale = 1.0 - wl

    ramp = _build_gamma_ramp(brightness=brightness, contrast=contrast,
                              r_scale=r_scale, g_scale=g_scale, b_scale=b_scale)
    _set_gamma_ramp(ramp)


def screen_color_filter(filter_code):
    """
    Apply a standalone display preset by numeric code.

    Behavior:
    - Codes -1 and 0..5 use native Windows Color Filters when possible.
    - Codes >=6 apply gamma-only presets (mutually exclusive with Windows filter).
    - Always apply fresh: turn off prior Windows filter before switching.

    Codes:
      -1 disable; 0 grayscale; 1 inverted; 2 gray-inverted; 3 deuteranopia; 4 protanopia; 5 tritanopia;
       6 warm; 7 dim; 8 low_contrast; 9 high_contrast; 10 warm_dim; 11 warm_low_contrast
    """
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)

    # Read current state
    current_active = _get_reg_dword(key, "Active", 0)

    # Resolve preset (fallback to grayscale if unknown)
    preset = FILTER_PRESETS.get(filter_code) or FILTER_PRESETS[0]

    # If -1, disable everything and return
    if preset["kind"] == "disable":
        _set_reg_dword(key, "HotkeyEnabled", 1)  # ensure hotkey works
        if current_active == 1:
            toggle_filter_hotkey()  # turn it off
            time.sleep(0.1)
        _set_reg_dword(key, "Active", 0)
        winreg.FlushKey(key)
        winreg.CloseKey(key)
        reset_gamma()  # reset gamma to default
        print("Display presets disabled: Color filter off and gamma reset.")
        return {"status": "success", "message": "Disabled all color filters and reset gamma to default"}

    if preset["kind"] == "win":
        # Native Windows filter path
        _set_reg_dword(key, "HotkeyEnabled", 1)
        _set_reg_dword(key, "FilterType", preset["filter_type"])
        winreg.FlushKey(key)

        # fresh apply: off then on
        if current_active == 1:
            toggle_filter_hotkey()
            time.sleep(0.15)
        # ensure no gamma modification is left from previous gamma presets
        reset_gamma()
        toggle_filter_hotkey()
        _set_reg_dword(key, "Active", 1)
        winreg.FlushKey(key)
        name = preset.get("name", str(preset["filter_type"]))
        print(f"Applied Windows color filter: {name} (type={preset['filter_type']}).")
        winreg.CloseKey(key)
        return {"status": "success", "message": f"Applied Windows color filter: {name}"}

    if preset["kind"] == "gamma":
        # Gamma-only path: ensure Windows filter is OFF
        _set_reg_dword(key, "HotkeyEnabled", 1)
        if current_active == 1:
            toggle_filter_hotkey()
            time.sleep(0.1)
            _set_reg_dword(key, "Active", 0)
            winreg.FlushKey(key)
        winreg.CloseKey(key)

        # Apply gamma preset
        _apply_gamma_preset(preset)
        preset_name = preset.get('name', 'custom')
        print(f"Applied gamma preset: {preset_name} (code={filter_code}).")
        return {"status": "success", "message": f"Applied gamma preset: {preset_name}"}