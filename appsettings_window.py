#!/usr/bin/env python3
"""
SitDeck Menubar — Settings Window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import yaml
from pathlib import Path


def open_settings_window(config_path: Path):
    """Open settings configuration window"""
    window = tk.Tk()
    window.title("⚙️ SitDeck Menubar — Settings")
    window.geometry("600x500")
    window.resizable(False, False)

    # Load current configuration
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # Create tabs
    notebook = ttk.Notebook(window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # SitDeck Tab
    sitdeck_frame = ttk.Frame(notebook)
    notebook.add(sitdeck_frame, text="🛰️ SitDeck")

    ttk.Label(sitdeck_frame, text="Webhook Port:").grid(
        row=0, column=0, sticky="w", pady=5
    )
    webhook_port = ttk.Entry(sitdeck_frame, width=30)
    webhook_port.insert(0, str(config.get("sitdeck", {}).get("webhook_port", 8080)))
    webhook_port.grid(row=0, column=1, pady=5)

    # Notifications Tab
    notify_frame = ttk.Frame(notebook)
    notebook.add(notify_frame, text="🔔 Notifications")

    notify_enabled = tk.BooleanVar(
        value=config.get("notifications", {}).get("enabled", True)
    )
    ttk.Checkbutton(
        notify_frame, text="Enable Notifications", variable=notify_enabled
    ).grid(row=0, column=0, pady=5)

    sound_enabled = tk.BooleanVar(
        value=config.get("notifications", {}).get("sound", True)
    )
    ttk.Checkbutton(notify_frame, text="Play Sound", variable=sound_enabled).grid(
        row=1, column=0, pady=5
    )

    # Filters Tab
    filters_frame = ttk.Frame(notebook)
    notebook.add(filters_frame, text="🔍 Filters")

    ttk.Label(filters_frame, text="Min Priority:").grid(
        row=0, column=0, sticky="w", pady=5
    )
    priority_var = tk.StringVar(
        value=config.get("filters", {}).get("min_priority", "medium")
    )
    ttk.Combobox(
        filters_frame,
        textvariable=priority_var,
        values=["low", "medium", "high", "critical"],
    ).grid(row=0, column=1, pady=5)

    # Save button
    def save_config():
        new_config = {
            "sitdeck": {"webhook_port": int(webhook_port.get())},
            "notifications": {
                "enabled": notify_enabled.get(),
                "sound": sound_enabled.get(),
            },
            "filters": {"min_priority": priority_var.get()},
        }

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(new_config, f, allow_unicode=True, default_flow_style=False)

        messagebox.showinfo("Saved", "Settings saved successfully!")
        window.destroy()

    ttk.Button(window, text="💾 Save", command=save_config).pack(pady=10)
    window.mainloop()