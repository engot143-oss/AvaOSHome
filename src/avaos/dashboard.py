"""
Parental dashboard for AVA OS.

Web interface for:
- Viewing conversation history
- Reviewing notifications
- Managing knowledge base
- Tracking learning progress
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, render_template_string, request, jsonify, send_file
from .memory import Memory
from .knowledge import KnowledgeBase
from .learning_analytics import LearningAnalytics
from .safety import SafetyManager
from .export import Exporter
from .insights import InsightEngine


class DashboardServer:
    """Web dashboard for AVA OS."""

    def __init__(
        self,
        memory_dir: Path = Path("~/.ava_os/memory").expanduser(),
        knowledge_dir: Path = Path("~/.ava_os/knowledge").expanduser(),
        port: int = 5000,
    ):
        self.memory_dir = Path(memory_dir)
        self.knowledge_dir = Path(knowledge_dir)
        self.port = port
        self.memory = Memory(self.memory_dir)
        self.kb = KnowledgeBase(self.knowledge_dir)
        self.analytics = LearningAnalytics(self.memory_dir)
        self.safety = SafetyManager(self.memory_dir)
        self.exporter = Exporter(self.memory_dir, self.knowledge_dir)
        self.insights = InsightEngine(self.memory_dir)
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """Register Flask routes."""

        @self.app.route("/")
        def dashboard():
            """Main dashboard."""
            return render_template_string(self._get_dashboard_html())

        @self.app.route("/api/stats")
        def get_stats():
            """Get conversation and notification stats."""
            history_file = self.memory_dir / "conversation_history.jsonl"
            notif_file = self.memory_dir / "notifications.log"

            turn_count = 0
            topics = {}
            if history_file.exists():
                for line in history_file.read_text().strip().split("\n"):
                    if line.strip():
                        turn_count += 1
                        data = json.loads(line)
                        topic = data.get("topic", "unknown")
                        topics[topic] = topics.get(topic, 0) + 1

            notif_count = 0
            if notif_file.exists():
                notif_count = len(
                    [l for l in notif_file.read_text().strip().split("\n") if l.strip()]
                )

            learned = self.kb.get_learned_topics()

            return jsonify(
                {
                    "conversation_turns": turn_count,
                    "notifications": notif_count,
                    "topics_discussed": topics,
                    "topics_learned": len(learned),
                }
            )

        @self.app.route("/api/conversations")
        def get_conversations():
            """Get conversation history with filtering."""
            topic = request.args.get("topic")
            limit = int(request.args.get("limit", 50))

            history_file = self.memory_dir / "conversation_history.jsonl"
            if not history_file.exists():
                return jsonify([])

            conversations = []
            for line in history_file.read_text().strip().split("\n"):
                if not line.strip():
                    continue
                data = json.loads(line)
                if topic and data.get("topic") != topic:
                    continue
                conversations.append(data)

            # Return most recent first
            return jsonify(conversations[-limit:][::-1])

        @self.app.route("/api/notifications")
        def get_notifications():
            """Get parent notifications."""
            limit = int(request.args.get("limit", 50))
            notif_file = self.memory_dir / "notifications.log"

            if not notif_file.exists():
                return jsonify([])

            notifications = []
            for line in notif_file.read_text().strip().split("\n"):
                if not line.strip():
                    continue
                # Parse "[timestamp] TOPIC: message"
                parts = line.split("] ", 1)
                if len(parts) == 2:
                    timestamp = parts[0][1:]  # remove leading [
                    rest = parts[1].split(": ", 1)
                    if len(rest) == 2:
                        topic, message = rest
                        notifications.append(
                            {
                                "timestamp": timestamp,
                                "topic": topic,
                                "message": message,
                            }
                        )

            return jsonify(notifications[-limit:][::-1])

        @self.app.route("/api/knowledge")
        def get_knowledge():
            """Get knowledge base facts for a given age."""
            age = int(request.args.get("age", 10))
            topic = request.args.get("topic")

            facts = self.kb.get_facts_for_age(age, topic=topic)
            return jsonify(
                [
                    {
                        "id": f.id,
                        "title": f.title,
                        "explanation": f.explanation,
                        "complexity": f.complexity.name,
                        "topic": f.topic,
                        "verified": f.verified,
                    }
                    for f in facts
                ]
            )

        @self.app.route("/api/learned")
        def get_learned():
            """Get topics daughter has learned."""
            learned = self.kb.get_learned_topics()
            return jsonify(
                [
                    {
                        "topic": l.topic,
                        "fact_id": l.fact_id,
                        "learned_at_age": l.learned_at_age,
                        "date_learned": l.date_learned,
                    }
                    for l in learned
                ]
            )

        @self.app.route("/api/analytics")
        def get_analytics():
            """Get learning analytics data."""
            all_topics = ["nursing", "finance", "life_skills", "medical"]
            engagements = self.analytics.get_topic_engagement()
            mastery = self.analytics.get_mastery_levels()
            streaks = self.analytics.get_learning_streaks()

            return jsonify(
                {
                    "topics": [
                        {
                            "topic": e.topic,
                            "times_discussed": e.times_discussed,
                            "total_messages": e.total_messages,
                            "messages_per_discussion": e.messages_per_discussion,
                            "mastery_level": mastery.get(e.topic, 1),
                            "current_streak": streaks.get(e.topic, 0),
                            "first_discussed": e.first_discussed,
                            "last_discussed": e.last_discussed,
                        }
                        for e in engagements
                    ],
                    "report": {
                        "total_conversations": len(self.memory.load_history()),
                        "unique_topics": len(engagements),
                        "learning_efficiency": len(engagements) / len(all_topics),
                    },
                }
            )

        @self.app.route("/api/recommendations")
        def get_recommendations():
            """Get learning recommendations."""
            recommendations = self.analytics.get_recommendations()
            return jsonify({"recommendations": recommendations})

        @self.app.route("/api/safety")
        def get_safety_stats():
            """Get safety statistics."""
            stats = self.safety.get_safety_stats()
            return jsonify(stats)

        @self.app.route("/api/insights")
        def get_insights():
            """Get advanced insights."""
            summary = self.insights.get_insights_summary()
            return jsonify(summary)

        @self.app.route("/api/insights/emotional-trend")
        def get_emotional_trend():
            """Get emotional trend."""
            days = int(request.args.get("days", 7))
            trend = self.insights.get_emotional_trend(days)
            return jsonify(trend)

        @self.app.route("/api/insights/velocity")
        def get_learning_velocity():
            """Get learning velocity."""
            velocity = self.insights.calculate_learning_velocity()
            return jsonify(velocity)

        @self.app.route("/api/insights/patterns")
        def get_patterns():
            """Get engagement patterns."""
            patterns = self.insights.get_engagement_patterns()
            return jsonify(patterns)

        @self.app.route("/api/insights/stress")
        def get_stress_indicators():
            """Get stress indicators."""
            indicators = self.insights.identify_stress_indicators()
            return jsonify({"indicators": indicators})

        @self.app.route("/api/export/conversations")
        def export_conversations():
            """Export conversations as JSON or CSV."""
            fmt = request.args.get("format", "json")
            if fmt == "csv":
                data = self.exporter.export_conversations_csv()
                return (
                    data,
                    200,
                    {"Content-Type": "text/csv",
                     "Content-Disposition": "attachment; filename=conversations.csv"},
                )
            else:
                data = self.exporter.export_conversations_json()
                return (
                    data,
                    200,
                    {"Content-Type": "application/json",
                     "Content-Disposition": "attachment; filename=conversations.json"},
                )

        @self.app.route("/api/export/analytics")
        def export_analytics():
            """Export analytics data."""
            data = self.exporter.export_analytics_json()
            return (
                data,
                200,
                {"Content-Type": "application/json",
                 "Content-Disposition": "attachment; filename=analytics.json"},
            )

        @self.app.route("/api/export/knowledge-base")
        def export_knowledge_base():
            """Export knowledge base."""
            data = self.exporter.export_knowledge_base_json()
            return (
                data,
                200,
                {"Content-Type": "application/json",
                 "Content-Disposition": "attachment; filename=knowledge_base.json"},
            )

        @self.app.route("/api/export/full-backup")
        def export_full_backup():
            """Export complete system backup."""
            data = self.exporter.export_full_backup_json()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return (
                data,
                200,
                {"Content-Type": "application/json",
                 "Content-Disposition": f"attachment; filename=ava_backup_{timestamp}.json"},
            )

        @self.app.route("/api/export/summary")
        def export_summary():
            """Get summary of what will be exported."""
            summary = self.exporter.get_backup_summary()
            return jsonify(summary)

        @self.app.route("/manifest.json")
        def get_manifest():
            """PWA manifest."""
            return jsonify(
                {
                    "name": "AVA OS - Parental Dashboard",
                    "short_name": "AVA OS",
                    "description": "AI guidance system for your daughter with hallucination checking",
                    "start_url": "/",
                    "scope": "/",
                    "display": "standalone",
                    "background_color": "#ffffff",
                    "theme_color": "#667eea",
                    "orientation": "portrait-primary",
                    "icons": [
                        {
                            "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 192 192'><rect fill='%23667eea' width='192' height='192'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='100' font-weight='bold' fill='white' font-family='system-ui'>A</text></svg>",
                            "sizes": "192x192",
                            "type": "image/svg+xml",
                            "purpose": "any",
                        },
                        {
                            "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect fill='%23667eea' width='512' height='512'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='280' font-weight='bold' fill='white' font-family='system-ui'>A</text></svg>",
                            "sizes": "512x512",
                            "type": "image/svg+xml",
                            "purpose": "any maskable",
                        },
                    ],
                    "screenshots": [
                        {
                            "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 540 720'><rect fill='%23667eea' width='540' height='720'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='100' font-weight='bold' fill='white' font-family='system-ui'>AVA Dashboard</text></svg>",
                            "sizes": "540x720",
                            "type": "image/svg+xml",
                            "form_factor": "narrow",
                        },
                    ],
                    "shortcuts": [
                        {
                            "name": "View Conversations",
                            "short_name": "Conversations",
                            "description": "View chat history",
                            "url": "/?tab=conversations",
                            "icons": [],
                        },
                        {
                            "name": "View Analytics",
                            "short_name": "Analytics",
                            "description": "View learning progress",
                            "url": "/?tab=analytics",
                            "icons": [],
                        },
                    ],
                }
            )

        @self.app.route("/sw.js")
        def get_service_worker():
            """Service worker for offline support."""
            return (
                """
const CACHE_NAME = 'ava-os-v1';
const urlsToCache = ['/', '/manifest.json'];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') {
        return;
    }

    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request).then(response => {
                return caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, response.clone());
                    return response;
                });
            }).catch(() => {
                return caches.match('/');
            });
        })
    );
});
""",
                200,
                {"Content-Type": "application/javascript"},
            )

    def _get_dashboard_html(self) -> str:
        """Return the dashboard HTML."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#667eea">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="AVA OS">
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 180 180'><rect fill='%23667eea' width='180' height='180'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='80' font-weight='bold' fill='white' font-family='system-ui'>A</text></svg>">
    <title>AVA OS - Parental Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        html, body {
            height: 100%;
            width: 100%;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 12px;
            font-size: 16px;
        }
        @media (min-width: 768px) {
            body {
                padding: 20px;
            }
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        @media (min-width: 768px) {
            header {
                padding: 30px;
                margin-bottom: 20px;
            }
        }
        h1 {
            color: #333;
            margin-bottom: 8px;
            font-size: 24px;
        }
        @media (min-width: 768px) {
            h1 {
                font-size: 32px;
                margin-bottom: 10px;
            }
        }
        .subtitle {
            color: #666;
            font-size: 13px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-bottom: 15px;
        }
        @media (min-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
        }
        .stat-card {
            background: white;
            padding: 16px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        @media (min-width: 768px) {
            .stat-card {
                padding: 20px;
            }
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        @media (min-width: 768px) {
            .stat-value {
                font-size: 32px;
            }
        }
        .stat-label {
            color: #666;
            font-size: 12px;
        }
        @media (min-width: 768px) {
            .stat-label {
                font-size: 14px;
            }
        }
        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
            background: white;
            padding: 8px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow-x: auto;
        }
        .tab-button {
            padding: 10px 16px;
            border: none;
            background: transparent;
            cursor: pointer;
            color: #666;
            font-weight: 500;
            border-bottom: 2px solid transparent;
            transition: all 0.3s;
            white-space: nowrap;
            font-size: 14px;
            touch-action: manipulation;
            min-height: 44px;
        }
        @media (min-width: 768px) {
            .tab-button {
                padding: 10px 20px;
                font-size: 16px;
            }
            .tabs {
                margin-bottom: 20px;
                padding: 10px;
            }
        }
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-button:hover, .tab-button:focus {
            color: #667eea;
            outline: none;
        }
        .tab-content {
            display: none;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .tab-content.active {
            display: block;
        }
        .conversation-item, .notification-item, .fact-item {
            padding: 12px;
            border-left: 4px solid #667eea;
            margin-bottom: 8px;
            background: #f9f9f9;
            border-radius: 5px;
            word-wrap: break-word;
        }
        @media (min-width: 768px) {
            .conversation-item, .notification-item, .fact-item {
                padding: 15px;
                margin-bottom: 10px;
            }
        }
        .conversation-item .role {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
            font-size: 14px;
        }
        .conversation-item .text {
            color: #333;
            margin-bottom: 5px;
            font-size: 14px;
            line-height: 1.4;
        }
        .conversation-item .meta {
            font-size: 11px;
            color: #999;
        }
        @media (min-width: 768px) {
            .conversation-item .text {
                font-size: 15px;
            }
            .conversation-item .meta {
                font-size: 12px;
            }
        }
        .notification-item {
            border-left-color: #ff6b6b;
        }
        .notification-item .topic {
            font-weight: bold;
            color: #ff6b6b;
            margin-bottom: 5px;
        }
        .notification-item .message {
            color: #333;
            margin-bottom: 5px;
        }
        .notification-item .timestamp {
            font-size: 12px;
            color: #999;
        }
        .fact-item {
            border-left-color: #51cf66;
        }
        .fact-item .title {
            font-weight: bold;
            color: #51cf66;
            margin-bottom: 5px;
        }
        .fact-item .explanation {
            color: #333;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .fact-item .meta {
            font-size: 12px;
            color: #999;
        }
        .loading {
            text-align: center;
            color: #999;
            padding: 20px;
        }
        .empty {
            text-align: center;
            color: #999;
            padding: 40px 20px;
        }
        .filter-bar {
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .filter-bar select, .filter-bar input {
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            min-height: 44px;
        }
        @media (min-width: 768px) {
            .filter-bar select, .filter-bar input {
                min-height: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>AVA OS - Parental Dashboard</h1>
            <p class="subtitle">Monitor conversations, review notifications, and manage your daughter's learning</p>
        </header>

        <div class="stats-grid" id="statsGrid">
            <div class="loading">Loading stats...</div>
        </div>

        <div class="tabs">
            <button class="tab-button active" onclick="showTab('conversations')">Conversations</button>
            <button class="tab-button" onclick="showTab('notifications')">Notifications</button>
            <button class="tab-button" onclick="showTab('analytics')">Analytics</button>
            <button class="tab-button" onclick="showTab('knowledge')">Knowledge Base</button>
            <button class="tab-button" onclick="showTab('learned')">Learning Progress</button>
        </div>

        <div id="conversations" class="tab-content active">
            <div class="filter-bar">
                <select id="topicFilter" onchange="loadConversations()">
                    <option value="">All Topics</option>
                    <option value="nursing">Nursing</option>
                    <option value="finance">Finance</option>
                    <option value="life_skills">Life Skills</option>
                    <option value="medical">Medical</option>
                </select>
            </div>
            <div id="conversationsList" class="loading">Loading conversations...</div>
        </div>

        <div id="notifications" class="tab-content">
            <div id="notificationsList" class="loading">Loading notifications...</div>
        </div>

        <div id="analytics" class="tab-content">
            <div id="analyticsContent" class="loading">Loading analytics...</div>
        </div>

        <div id="knowledge" class="tab-content">
            <div class="filter-bar">
                <input type="number" id="ageInput" value="10" min="8" max="18" style="width: 80px; padding: 8px;">
                <select id="kbTopicFilter" onchange="loadKnowledge()">
                    <option value="">All Topics</option>
                    <option value="nursing">Nursing</option>
                    <option value="finance">Finance</option>
                    <option value="life_skills">Life Skills</option>
                </select>
            </div>
            <div id="knowledgeList" class="loading">Loading knowledge base...</div>
        </div>

        <div id="learned" class="tab-content">
            <div id="learnedList" class="loading">Loading learning progress...</div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');

            // Load data if needed
            if (tabName === 'conversations') loadConversations();
            if (tabName === 'notifications') loadNotifications();
            if (tabName === 'knowledge') loadKnowledge();
            if (tabName === 'learned') loadLearned();
        }

        function loadStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    const html = `
                        <div class="stat-card">
                            <div class="stat-value">${data.conversation_turns}</div>
                            <div class="stat-label">Conversation Turns</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.notifications}</div>
                            <div class="stat-label">Notifications</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.topics_learned}</div>
                            <div class="stat-label">Topics Learned</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${Object.keys(data.topics_discussed).length}</div>
                            <div class="stat-label">Topics Discussed</div>
                        </div>
                    `;
                    document.getElementById('statsGrid').innerHTML = html;
                });
        }

        function loadConversations() {
            const topic = document.getElementById('topicFilter').value;
            const url = `/api/conversations${topic ? '?topic=' + topic : ''}`;

            fetch(url)
                .then(r => r.json())
                .then(data => {
                    if (data.length === 0) {
                        document.getElementById('conversationsList').innerHTML = '<div class="empty">No conversations yet</div>';
                        return;
                    }
                    const html = data.map(turn => `
                        <div class="conversation-item">
                            <div class="role">${turn.role === 'user' ? 'Your daughter' : 'AVA'}</div>
                            <div class="text">${escapeHtml(turn.text)}</div>
                            <div class="meta">
                                Topic: ${turn.topic} | ${new Date(turn.timestamp).toLocaleString()}
                            </div>
                        </div>
                    `).join('');
                    document.getElementById('conversationsList').innerHTML = html;
                });
        }

        function loadNotifications() {
            fetch('/api/notifications')
                .then(r => r.json())
                .then(data => {
                    if (data.length === 0) {
                        document.getElementById('notificationsList').innerHTML = '<div class="empty">No notifications</div>';
                        return;
                    }
                    const html = data.map(n => `
                        <div class="notification-item">
                            <div class="topic">${n.topic}</div>
                            <div class="message">${escapeHtml(n.message)}</div>
                            <div class="timestamp">${new Date(n.timestamp).toLocaleString()}</div>
                        </div>
                    `).join('');
                    document.getElementById('notificationsList').innerHTML = html;
                });
        }

        function loadKnowledge() {
            const age = document.getElementById('ageInput').value;
            const topic = document.getElementById('kbTopicFilter').value;
            const url = `/api/knowledge?age=${age}${topic ? '&topic=' + topic : ''}`;

            fetch(url)
                .then(r => r.json())
                .then(data => {
                    if (data.length === 0) {
                        document.getElementById('knowledgeList').innerHTML = '<div class="empty">No facts for this age/topic</div>';
                        return;
                    }
                    const html = data.map(fact => `
                        <div class="fact-item">
                            <div class="title">${fact.title}</div>
                            <div class="explanation">${fact.explanation}</div>
                            <div class="meta">
                                Complexity: ${fact.complexity} | Topic: ${fact.topic} | Verified: ${fact.verified ? 'Yes' : 'No'}
                            </div>
                        </div>
                    `).join('');
                    document.getElementById('knowledgeList').innerHTML = html;
                });
        }

        function loadAnalytics() {
            fetch('/api/analytics')
                .then(r => r.json())
                .then(data => {
                    if (data.topics.length === 0) {
                        document.getElementById('analyticsContent').innerHTML = '<div class="empty">No analytics data yet</div>';
                        return;
                    }

                    const html = `
                        <div style="margin-bottom: 20px;">
                            <h3 style="color: #667eea; margin-bottom: 15px;">Learning Summary</h3>
                            <div class="stat-card" style="margin-bottom: 15px;">
                                <div style="margin-bottom: 10px;">
                                    <strong>Total Conversations:</strong> ${data.report.total_conversations}
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <strong>Topics Engaged:</strong> ${data.report.unique_topics}
                                </div>
                                <div>
                                    <strong>Learning Efficiency:</strong> ${(data.report.learning_efficiency * 100).toFixed(1)}%
                                </div>
                            </div>
                        </div>

                        <div>
                            <h3 style="color: #667eea; margin-bottom: 15px;">Topic Engagement</h3>
                            ${data.topics.map(topic => `
                                <div class="fact-item">
                                    <div class="title">${topic.topic.replace('_', ' ').toUpperCase()}</div>
                                    <div style="font-size: 14px; color: #333; margin-bottom: 5px;">
                                        Discussed: ${topic.times_discussed}x |
                                        Messages: ${topic.total_messages} |
                                        Avg: ${topic.messages_per_discussion.toFixed(1)}/discussion
                                    </div>
                                    <div style="font-size: 12px; color: #666;">
                                        Mastery Level: ${topic.mastery_level}/5 |
                                        Current Streak: ${topic.current_streak} days
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    document.getElementById('analyticsContent').innerHTML = html;
                });
        }

        function loadLearned() {
            fetch('/api/learned')
                .then(r => r.json())
                .then(data => {
                    if (data.length === 0) {
                        document.getElementById('learnedList').innerHTML = '<div class="empty">No topics learned yet</div>';
                        return;
                    }
                    const byTopic = {};
                    data.forEach(item => {
                        if (!byTopic[item.topic]) byTopic[item.topic] = [];
                        byTopic[item.topic].push(item);
                    });

                    const html = Object.entries(byTopic).map(([topic, items]) => `
                        <div style="margin-bottom: 20px;">
                            <h3 style="color: #667eea; margin-bottom: 10px;">${topic}</h3>
                            ${items.map(item => `
                                <div class="fact-item">
                                    <div class="meta">${item.fact_id} • Learned at age ${item.learned_at_age}</div>
                                </div>
                            `).join('')}
                        </div>
                    `).join('');
                    document.getElementById('learnedList').innerHTML = html;
                });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // PWA service worker registration
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js').catch(err => {
                console.log('Service worker registration failed:', err);
            });
        }

        // Load stats on page load
        loadStats();
        loadConversations();
    </script>
</body>
</html>
"""

    def run(self, debug: bool = False):
        """Start the dashboard server."""
        print(f"\n*** AVA OS Parental Dashboard ***")
        print(f"Starting server on http://localhost:{self.port}")
        print(f"Press Ctrl+C to stop\n")
        self.app.run(debug=debug, port=self.port, use_reloader=False)


if __name__ == "__main__":
    server = DashboardServer()
    server.run(debug=True)
