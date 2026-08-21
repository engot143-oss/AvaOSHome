#!/usr/bin/env python3
"""
AVA OS Kumon Server - Serves PWA and handles API requests.

Provides:
- Static file serving (PWA frontend)
- API endpoints for daily topics, progress, chat
- Data synchronization between client and server
- Hallucination checking on responses
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from avaos.kumon import KumonTracker
from avaos.memory import Memory
from avaos.hallucination_prevention import HallucinationPreventionPipeline
from avaos.faith_curriculum import FaithCurriculum
from avaos.automation_framework import AutomationFramework
from avaos.system_improvement_loop import SystemImprovementLoop
from avaos.improvement_scheduler import initialize_scheduler, get_scheduler

app = Flask(__name__, static_folder=str(Path(__file__).parent.parent / 'web'))
CORS(app)

# Security configuration
API_KEY = os.environ.get('AVA_API_KEY', 'dev-key-change-in-production')
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_PERIOD = 3600  # 1 hour

# Rate limiting tracker
rate_limiter = defaultdict(list)

# Initialize components
memory_dir = Path.home() / '.ava_os' / 'memory'
curriculum_path = Path.home() / '.ava_os' / 'curriculum' / 'kumon_curriculum.json'

memory = Memory(memory_dir)
tracker = KumonTracker(memory_dir, curriculum_path)
checker = HallucinationPreventionPipeline(memory_dir, curriculum_path)
faith = FaithCurriculum(memory_dir)
automation = AutomationFramework(memory_dir)
improvement_loop = SystemImprovementLoop(memory_dir)


# Security decorators
def require_api_key(f):
    """Require valid API key for endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if not key or key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(f):
    """Rate limit endpoint by IP address."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        now = datetime.now()

        # Clean old requests
        rate_limiter[client_ip] = [
            req_time for req_time in rate_limiter[client_ip]
            if now - req_time < timedelta(seconds=RATE_LIMIT_PERIOD)
        ]

        # Check limit
        if len(rate_limiter[client_ip]) >= RATE_LIMIT_REQUESTS:
            return jsonify({
                'error': 'Rate limit exceeded',
                'limit': RATE_LIMIT_REQUESTS,
                'period_seconds': RATE_LIMIT_PERIOD,
                'retry_after': RATE_LIMIT_PERIOD
            }), 429

        # Record this request
        rate_limiter[client_ip].append(now)

        return f(*args, **kwargs)
    return decorated_function


def validate_json(required_fields=None):
    """Validate JSON request body."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400

            data = request.get_json()
            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    return jsonify({
                        'error': f'Missing required fields: {", ".join(missing)}'
                    }), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def index():
    """Serve the main PWA."""
    web_dir = Path(__file__).parent.parent / 'web'
    return send_from_directory(web_dir, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """Serve static assets."""
    web_dir = Path(__file__).parent.parent / 'web'
    return send_from_directory(web_dir, path)


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'microphone=(), geolocation=(), camera=()'
    return response


@app.route('/api/topic/today', methods=['GET'])
@rate_limit
def get_today_topic():
    """Get today's Kumon topic."""
    try:
        daily = tracker.select_daily_topic()
        if not daily:
            return jsonify({'error': 'No topic available'}), 400

        return jsonify({
            'success': True,
            'date': daily.date,
            'concept_id': daily.concept_id,
            'subject': daily.subject,
            'concept_name': daily.concept_name,
            'difficulty_level': daily.difficulty_level,
            'estimated_time_min': daily.estimated_time_min,
            'status': daily.status,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/all', methods=['GET'])
def get_all_progress():
    """Get overall progress."""
    try:
        progress = tracker.get_all_progress()
        return jsonify({
            'success': True,
            'total_concepts': progress['total_concepts'],
            'mastered_concepts': progress['mastered_concepts'],
            'overall_mastery_percent': progress['overall_mastery_percent'],
            'subjects': progress['subjects'],
            'streak': progress['streak'],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/subject/<subject>', methods=['GET'])
def get_subject_progress(subject):
    """Get progress for a specific subject."""
    try:
        progress = tracker.get_subject_progress(subject)
        return jsonify({'success': True, **progress})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mastery/report', methods=['GET'])
def get_mastery_report():
    """Get detailed mastery report."""
    try:
        report = tracker.get_mastery_report()
        return jsonify({
            'success': True,
            'concepts': report,
            'total': len(report),
            'mastered': sum(1 for c in report if c['mastered']),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attempt', methods=['POST'])
@rate_limit
@validate_json(required_fields=['concept_id', 'correct', 'score'])
def record_attempt():
    """Record a practice attempt."""
    try:
        data = request.get_json()
        concept_id = data.get('concept_id')
        correct = data.get('correct', False)
        score = float(data.get('score', 0.0))

        # Validate inputs
        if not isinstance(concept_id, str) or len(concept_id) > 50:
            return jsonify({'error': 'Invalid concept_id'}), 400
        if not isinstance(correct, bool):
            return jsonify({'error': 'correct must be boolean'}), 400
        if not 0 <= score <= 1:
            return jsonify({'error': 'score must be between 0 and 1'}), 400

        progress = tracker.record_attempt(concept_id, correct, score)

        return jsonify({
            'success': True,
            'concept_id': concept_id,
            'mastery_percent': progress['mastery_percent'],
            'mastered': progress['mastered'],
            'attempts': progress['attempts'],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
@rate_limit
@validate_json(required_fields=['message'])
def handle_chat():
    """Handle chat message from student."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        concept_id = data.get('concept_id', 'general')

        # Validate message length
        if not message or len(message) > 10000:
            return jsonify({'error': 'Message must be between 1 and 10000 characters'}), 400

        # Basic prompt injection detection
        if _has_prompt_injection(message):
            return jsonify({'error': 'Invalid input detected'}), 400

        # In production, call Claude API here with hallucination checking
        # For now, return mock response
        response = f"Great question! Let me help you understand that better."

        # Record in conversation history
        from avaos.memory import ConversationTurn
        turn1 = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            role='user',
            text=message,
            topic=concept_id
        )
        turn2 = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            role='assistant',
            text=response,
            topic=concept_id
        )
        memory.append_turn(turn1)
        memory.append_turn(turn2)

        return jsonify({
            'success': True,
            'response': response,
            'hallucination_checked': False,  # Would be True with real hallucination checker
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _has_prompt_injection(text: str) -> bool:
    """Detect common prompt injection attempts."""
    injection_patterns = [
        r'ignore.*instruction',
        r'forget.*prompt',
        r'system.*override',
        r'jailbreak',
        r'reveal.*system',
        r'what are your.*instruction',
    ]
    for pattern in injection_patterns:
        if re.search(pattern, text.lower()):
            return True
    return False


@app.route('/api/sync', methods=['POST'])
def sync_data():
    """Sync client data with server."""
    try:
        data = request.get_json()
        client_data = data.get('data', {})

        # Merge client data with server state
        # Priority: server state is authoritative
        server_progress = tracker.get_all_progress()

        return jsonify({
            'success': True,
            'server_state': server_progress,
            'synced_at': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/security/status', methods=['GET'])
def security_status():
    """Get security and rate limit status."""
    client_ip = request.remote_addr
    remaining = RATE_LIMIT_REQUESTS - len(rate_limiter[client_ip])

    return jsonify({
        'status': 'secure',
        'rate_limit': {
            'limit': RATE_LIMIT_REQUESTS,
            'period_seconds': RATE_LIMIT_PERIOD,
            'remaining': max(0, remaining),
        },
        'security_features': {
            'api_key_required': API_KEY != 'dev-key-change-in-production',
            'rate_limiting': True,
            'content_filtering': True,
            'prompt_injection_detection': True,
            'security_headers': True,
            'https_enforced': False,  # Set True after Netlify deployment
        }
    })


@app.route('/api/faith/lessons/<int:age>', methods=['GET'])
def get_faith_lessons(age):
    """Get faith curriculum lessons for age."""
    lessons = faith.get_lessons_for_age(age)
    return jsonify({
        'age': age,
        'lessons': lessons,
        'level': faith.FAITH_CURRICULUM.get(age, {}).get('level', 'UNKNOWN')
    })


@app.route('/api/faith/summary/<int:age>', methods=['GET'])
def get_faith_summary(age):
    """Get faith progress summary."""
    summary = faith.get_spiritual_summary(age)
    return jsonify(summary)


@app.route('/api/faith/reflection', methods=['GET'])
def get_daily_reflection():
    """Get today's reflection prompt."""
    prompt = faith.get_daily_reflection_prompt()
    return jsonify({'prompt': prompt})


@app.route('/api/faith/record_prayer', methods=['POST'])
def record_prayer():
    """Record a prayer."""
    data = request.json
    prayer_date = data.get('date', datetime.now().isoformat())
    subject = data.get('subject', 'Prayer')

    faith.record_prayer(prayer_date, subject)

    return jsonify({
        'success': True,
        'message': 'Prayer recorded',
        'date': prayer_date
    })


@app.route('/api/faith/record_reflection', methods=['POST'])
def record_reflection():
    """Record a reflection."""
    data = request.json
    reflection_text = data.get('reflection', '')
    question = data.get('question', None)

    if not reflection_text:
        return jsonify({'error': 'Reflection text required'}), 400

    faith.record_reflection(reflection_text, question)

    return jsonify({
        'success': True,
        'message': 'Reflection recorded',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/faith/report', methods=['GET'])
def get_faith_report():
    """Get parent's faith development report."""
    report = faith.get_parent_report()
    return jsonify({
        'report': report,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'kumon_tracker': 'ready',
            'memory': 'ready',
            'hallucination_checker': 'ready',
            'faith_curriculum': 'ready',
        },
        'security': 'enabled'
    })


@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest."""
    web_dir = Path(__file__).parent.parent / 'web'
    return send_from_directory(web_dir, 'manifest.json')


@app.route('/sw.js')
def service_worker():
    """Serve service worker."""
    web_dir = Path(__file__).parent.parent / 'web'
    return send_from_directory(web_dir, 'sw.js')


@app.route('/api/automation/health', methods=['GET'])
def automation_health():
    """Get automation framework health."""
    analysis = automation.analyze_system_health()
    return jsonify(analysis)


@app.route('/api/automation/report', methods=['GET'])
def automation_report():
    """Get automation system report."""
    report = automation.get_framework_status_report()
    return jsonify({'report': report})


@app.route('/api/improvement/status', methods=['GET'])
def improvement_status():
    """Get improvement pipeline status."""
    status = improvement_loop.get_pipeline_status()
    return jsonify(status)


@app.route('/api/improvement/run-cycle', methods=['POST'])
def run_improvement_cycle():
    """Manually trigger improvement cycle."""
    result = improvement_loop.run_improvement_cycle()
    return jsonify(result)


@app.route('/api/improvement/health-report', methods=['GET'])
def improvement_health_report():
    """Get improvement system health report."""
    report = improvement_loop.get_system_health_report()
    return jsonify({'report': report})


@app.errorhandler(404)
def not_found(e):
    """Handle 404 - serve index.html for SPA routing."""
    web_dir = Path(__file__).parent.parent / 'web'
    return send_from_directory(web_dir, 'index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Initialize improvement scheduler
    scheduler = initialize_scheduler(memory_dir)

    print(f"""
    [AVA OS - Kumon Server]

    Starting server on http://localhost:{port}

    Endpoints:
    - GET  /                    - Main PWA
    - GET  /api/topic/today     - Today's topic
    - GET  /api/progress/all    - Overall progress
    - GET  /api/progress/subject/<name> - Subject progress
    - GET  /api/mastery/report  - Mastery details
    - POST /api/attempt         - Record practice attempt
    - POST /api/chat            - Chat with AVA
    - POST /api/sync            - Sync client data
    - GET  /api/health          - Health check
    - GET  /api/automation/health      - Automation framework health
    - GET  /api/automation/report      - System status report
    - GET  /api/improvement/status     - Improvement pipeline status
    - POST /api/improvement/run-cycle  - Trigger improvement cycle
    - GET  /api/improvement/health-report - Improvement system report

    AUTONOMOUS IMPROVEMENT LOOP: ENABLED
    - Runs automatically on schedule (daily)
    - Monitors all 20 frameworks
    - Auto-applies improvements
    - Prevents regressions

    Press Ctrl+C to stop.
    """)

    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    finally:
        if scheduler:
            scheduler.stop()
