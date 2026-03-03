#!/usr/bin/env python3
"""
SitDeck Menubar — Menu Bar Application
"""

import rumps
import threading
import asyncio
import yaml
import json
import subprocess
from pathlib import Path
from datetime import datetime
from webhook_server import WebhookServer
from notifications import send_notification
from settings_window import open_settings_window
from statistics_window import open_statistics_window
from geofilter import GeoFilter
from scheduler import ReportScheduler
from updater import AutoUpdater


class SitDeckMenuBarApp(rumps.App):
    """Main menu bar application class"""

    def __init__(self):
        super().__init__("🛰️", title=None)

        # Paths
        self.install_dir = Path.home() / ".sitdeck-menubar"
        self.config_path = self.install_dir / "config.yaml"
        self.alerts_file = self.install_dir / "data" / "alerts.json"

        # Load configuration
        self.config = self.load_config()

        # Status
        self.alerts_count = 0
        self.alerts_today = 0
        self.last_alert_time = None
        self.monitoring_active = True

        # Geo-filter
        geo_config = self.config.get("filters", {}).get("geofencing", {})
        self.geo_filter = (
            GeoFilter(regions=geo_config.get("regions", []))
            if geo_config.get("enabled")
            else GeoFilter()
        )

        # Setup menu
        self.setup_menu()

        # Start webhook server
        self.start_webhook_server()

        # Report scheduler
        self.scheduler = ReportScheduler(self.config)
        self.scheduler.start()

        # Update timer
        self.timer = rumps.Timer(self.update_stats, 60)
        self.timer.start()

        # Check for updates
        if self.config.get("updater", {}).get("auto_check", True):
            self.check_update()

    def load_config(self):
        """Load configuration from YAML file"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def load_alerts_data(self):
        """Load alerts history from JSON file"""
        if self.alerts_file.exists():
            with open(self.alerts_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_alert(self, alert_data: dict):
        """Save alert to history file"""
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)

        alerts = self.load_alerts_data()
        alerts.append(
            {
                **alert_data,
                "timestamp": datetime.now().isoformat(),
                "received_at": datetime.now().isoformat(),
            }
        )

        # Keep last 1000 alerts
        alerts = alerts[-1000:]

        with open(self.alerts_file, "w", encoding="utf-8") as f:
            json.dump(alerts, f, ensure_ascii=False, indent=2)

    def setup_menu(self):
        """Setup menu bar items"""
        # Icon based on status
        self.icon = "🛰️" if self.monitoring_active else "⏸️"

        # Calculate statistics
        alerts_data = self.load_alerts_data()
        today = datetime.now().date()
        self.alerts_today = len(
            [
                a
                for a in alerts_data
                if datetime.fromisoformat(a["timestamp"]).date() == today
            ]
        )

        self.menu = [
            ("📊 Statistics", None),
            (f"  🔴 Critical: {self.count_by_priority('critical')}", None),
            (f"  🟠 High: {self.count_by_priority('high')}", None),
            (f"  🟡 Medium: {self.count_by_priority('medium')}", None),
            (f"  🟢 Low: {self.count_by_priority('low')}", None),
            ("─", None),
            (f"  Today: {self.alerts_today}", None),
            (f"  Last: {self.last_alert_time or 'None'}", None),
            ("─", None),
            (
                "⚡ Quick Actions",
                [
                    ("▶️ Resume", self.resume_monitoring)
                    if not self.monitoring_active
                    else None,
                    ("⏸️ Pause", self.pause_monitoring)
                    if self.monitoring_active
                    else None,
                    ("🔔 Test Notification", self.test_notification),
                    ("🔄 Reload Config", self.reload_config_callback),
                ],
            ),
            ("📊 Statistics & History", self.open_statistics),
            ("⚙️ Settings", self.open_settings),
            ("─", None),
            ("📂 Open Logs", self.open_logs),
            ("📁 Data Folder", self.open_data_folder),
            ("─", None),
            ("🚪 Quit", self.quit_callback),
        ]

        self.menu = self.clean_menu(self.menu)

    def clean_menu(self, menu):
        """Remove None items from menu"""
        cleaned = []
        for item in menu:
            if item is None:
                continue
            if isinstance(item, tuple) and len(item) == 2:
                label, action = item
                if isinstance(action, list):
                    action = self.clean_menu(action)
                    if action:
                        cleaned.append((label, action))
                else:
                    cleaned.append(item)
            else:
                cleaned.append(item)
        return cleaned

    def count_by_priority(self, priority: str) -> int:
        """Count alerts by priority for today"""
        alerts_data = self.load_alerts_data()
        today = datetime.now().date()
        return len(
            [
                a
                for a in alerts_data
                if datetime.fromisoformat(a["timestamp"]).date() == today
                and a.get("priority") == priority
            ]
        )

    def update_stats(self, sender):
        """Update statistics every minute"""
        self.setup_menu()

    def start_webhook_server(self):
        """Start webhook server in background thread"""
        port = self.config.get("sitdeck", {}).get("webhook_port", 8080)

        def run_server():
            server = WebhookServer(port=port, callback=self.on_alert)
            asyncio.run(server.run())

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

    def pause_monitoring(self, sender):
        """Pause alert monitoring"""
        self.monitoring_active = False
        self.setup_menu()
        send_notification("SitDeck Menubar", "Monitoring paused", "low")

    def resume_monitoring(self, sender):
        """Resume alert monitoring"""
        self.monitoring_active = True
        self.setup_menu()
        send_notification("SitDeck Menubar", "Monitoring resumed", "low")

    def test_notification(self, sender):
        """Send test notification"""
        send_notification(
            "SitDeck Menubar — Test",
            "Everything is working! ✅",
            "medium",
            "https://sitdeck.com",
        )

    def reload_config_callback(self, sender):
        """Reload configuration file"""
        self.config = self.load_config()
        send_notification("SitDeck Menubar", "Configuration reloaded", "low")

    def open_statistics(self, sender):
        """Open statistics window"""
        threading.Thread(
            target=lambda: open_statistics_window(self.config_path), daemon=True
        ).start()

    def open_settings(self, sender):
        """Open settings window"""
        threading.Thread(
            target=lambda: open_settings_window(self.config_path), daemon=True
        ).start()

    def open_logs(self, sender):
        """Open logs folder"""
        log_path = self.install_dir / "logs" / "app.log"
        if log_path.exists():
            subprocess.run(["open", str(log_path)])

    def open_data_folder(self, sender):
        """Open data folder"""
        data_path = self.install_dir / "data"
        data_path.mkdir(parents=True, exist_ok=True)
        subprocess.run(["open", str(data_path)])

    def on_alert(self, alert_data: dict):
        """Handle incoming alert from SitDeck"""
        if not self.monitoring_active:
            return

        # Geo-filtering
        if not self.geo_filter.filter_alert(alert_data):
            return

        # Save to history
        self.save_alert(alert_data)

        # Update UI
        self.last_alert_time = datetime.now().strftime("%H:%M:%S")
        self.setup_menu()

        # Send notification
        title = alert_data.get("title", "New Event")
        message = alert_data.get("description", "Check SitDeck for details")
        priority = alert_data.get("priority", "medium")

        send_notification(
            f"🛰️ SitDeck: {title}", message, priority, alert_data.get("url")
        )

    def check_update(self):
        """Check for application updates"""

        def check():
            updater = AutoUpdater()
            if updater.check_update():
                send_notification("SitDeck Menubar", "Update available!", "low")

        threading.Thread(target=check, daemon=True).start()

    def quit_callback(self, sender):
        """Quit application"""
        send_notification("SitDeck Menubar", "Application stopped", "low")
        self.quit(None)