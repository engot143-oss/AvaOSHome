"""
Tests for mobile optimization and PWA support.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.dashboard import DashboardServer
from avaos.knowledge import INITIAL_FACTS, KnowledgeBase


class TestMobileAndPWA(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_dir = Path(self.temp_dir.name) / "memory"
        self.knowledge_dir = Path(self.temp_dir.name) / "knowledge"
        self.memory_dir.mkdir()
        self.knowledge_dir.mkdir()

        # Initialize knowledge base
        kb = KnowledgeBase(self.knowledge_dir)
        for fact in INITIAL_FACTS:
            kb.add_fact(fact)

        self.server = DashboardServer(
            memory_dir=self.memory_dir,
            knowledge_dir=self.knowledge_dir,
            port=5001,
        )
        self.client = self.server.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dashboard_responsive(self):
        """Dashboard should load and include responsive meta tags."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        html = response.data.decode()
        self.assertIn("viewport", html)
        self.assertIn("initial-scale=1.0", html)
        self.assertIn("viewport-fit=cover", html)

    def test_pwa_manifest(self):
        """PWA manifest should be available and valid."""
        response = self.client.get("/manifest.json")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("name", data)
        self.assertIn("start_url", data)
        self.assertIn("display", data)
        self.assertIn("icons", data)
        self.assertEqual(data["display"], "standalone")
        self.assertEqual(data["theme_color"], "#667eea")

    def test_pwa_manifest_has_icons(self):
        """Manifest should include app icons."""
        response = self.client.get("/manifest.json")
        data = response.get_json()

        self.assertGreaterEqual(len(data["icons"]), 2)
        for icon in data["icons"]:
            self.assertIn("src", icon)
            self.assertIn("sizes", icon)
            self.assertIn("type", icon)

    def test_pwa_manifest_has_shortcuts(self):
        """Manifest should include app shortcuts."""
        response = self.client.get("/manifest.json")
        data = response.get_json()

        self.assertGreaterEqual(len(data["shortcuts"]), 1)
        for shortcut in data["shortcuts"]:
            self.assertIn("name", shortcut)
            self.assertIn("url", shortcut)

    def test_service_worker_available(self):
        """Service worker should be available."""
        response = self.client.get("/sw.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("self.addEventListener", response.data.decode())

    def test_service_worker_caching_logic(self):
        """Service worker should have caching logic."""
        response = self.client.get("/sw.js")
        js = response.data.decode()

        self.assertIn("CACHE_NAME", js)
        self.assertIn("addEventListener('install'", js)
        self.assertIn("addEventListener('fetch'", js)
        self.assertIn("caches.open", js)

    def test_apple_mobile_meta_tags(self):
        """Dashboard should include Apple mobile web app meta tags."""
        response = self.client.get("/")
        html = response.data.decode()

        self.assertIn("apple-mobile-web-app-capable", html)
        self.assertIn("apple-mobile-web-app-status-bar-style", html)
        self.assertIn("apple-mobile-web-app-title", html)

    def test_theme_color_meta_tag(self):
        """Dashboard should include theme color for mobile browsers."""
        response = self.client.get("/")
        html = response.data.decode()

        self.assertIn("theme-color", html)
        self.assertIn("#667eea", html)

    def test_responsive_grid_in_html(self):
        """Dashboard should have responsive grid layout."""
        response = self.client.get("/")
        html = response.data.decode()

        self.assertIn("grid", html)
        self.assertIn("auto-fit", html)

    def test_touch_friendly_buttons(self):
        """Dashboard should have touch-friendly button sizing."""
        response = self.client.get("/")
        html = response.data.decode()

        self.assertIn("touch-action", html)
        self.assertIn("min-height: 44px", html)


if __name__ == "__main__":
    unittest.main()
