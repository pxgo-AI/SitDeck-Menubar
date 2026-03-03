#!/usr/bin/env python3
"""
SitDeck Menubar — Webhook Server
"""

import asyncio
from aiohttp import web


class WebhookServer:
    """HTTP server for receiving SitDeck webhooks"""

    def __init__(self, port: int = 8080, callback=None):
        self.port = port
        self.callback = callback
        self.app = web.Application()
        self.app.router.add_post("/sitdeck-webhook", self.handle_webhook)
        self.app.router.add_get("/", self.handle_health)

    async def handle_webhook(self, request):
        """Handle incoming webhook from SitDeck"""
        try:
            data = await request.json()
            if self.callback:
                self.callback(data)
            return web.json_response({"status": "ok"})
        except Exception as e:
            return web.json_response(
                {"status": "error", "message": str(e)}, status=400
            )

    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "running", "port": self.port})

    async def run(self):
        """Start the webhook server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()
        print(f"🌐 Webhook server running on port {self.port}")

        while True:
            await asyncio.sleep(3600)