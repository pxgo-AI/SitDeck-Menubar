#!/usr/bin/env python3
"""
SitDeck Menubar — Native macOS Notifications
"""

import subprocess


def send_notification(
    title: str, message: str, priority: str = "medium", url: str = None
):
    """Send native macOS notification with sound"""

    sound_map = {
        "low": "Sosumi",
        "medium": "Ping",
        "high": "Glass",
        "critical": "Submarine",
    }
    sound = sound_map.get(priority, "Ping")

    script = f'''
    display notification "{message}" with title "{title}" sound name "{sound}"
    '''

    subprocess.run(["osascript", "-e", script], check=False)