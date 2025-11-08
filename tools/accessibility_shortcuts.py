import subprocess
import pyautogui


def _tasklist_text() -> str:
    """Return the output of 'tasklist' command as lowercase string, or empty string on error."""
    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True, check=False)
        return (result.stdout or "").lower()
    except Exception:
        return ""


def _is_running(name_variants, tasklist_cache: str | None = None) -> bool:
    """Return True if any of the name_variants is found in the running processes."""
    text = tasklist_cache if isinstance(tasklist_cache, str) else _tasklist_text()
    if not text:
        return False
    for name in name_variants:
        if name.lower() in text:
            return True
    return False


def accessibility_shortcuts(
    narrator: bool | None = None,
    live_captions: bool | None = None,
    onscreen_keyboard: bool | None = None,
    magnifier: bool | None = None,
):
    """
    Toggle Windows accessibility features based on flags.

    Semantics per flag:
      - True  -> toggle the feature once
      - False -> do nothing (leave as-is)
      - None  -> do nothing (leave as-is)

    Shortcuts used:
      - narrator: Win+Ctrl+Enter (toggle)
      - live_captions: Win+Ctrl+L (toggle)
      - onscreen_keyboard: Win+Ctrl+O (toggle)
      - magnifier: toggle by state (Magnify.exe running => Win+Esc to turn off; otherwise Win+= to turn on)

    Notes:
    - Only Magnifier needs state detection to implement a proper toggle since it
      does not have a single toggle shortcut.
    """

    if narrator is True:
        pyautogui.hotkey("win", "ctrl", "enter")

    if live_captions is True:
        pyautogui.hotkey("win", "ctrl", "l")

    if onscreen_keyboard is True:
        pyautogui.hotkey("win", "ctrl", "o")

    if magnifier is True:
        if _is_running(["magnify.exe", "magnify"]):
            pyautogui.hotkey("win", "esc")  # turn off
        else:
            pyautogui.hotkey("win", "=")    # turn on
