"""
Improvement Loop Scheduler - Starts and manages the autonomous improvement cycle.

Runs in background, checking if improvements should run based on schedule.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from .system_improvement_loop import SystemImprovementLoop
from .automation_framework import AutomationFramework


class ImprovementScheduler:
    """Manages autonomous improvement cycle scheduling."""

    def __init__(self, memory_dir: Path, run_in_background: bool = True):
        self.memory_dir = memory_dir
        self.improvement_loop = SystemImprovementLoop(memory_dir)
        self.automation = AutomationFramework(memory_dir)
        self.running = False
        self.thread: Optional[threading.Thread] = None

        if run_in_background:
            self.start()

    def start(self) -> None:
        """Start the improvement scheduler."""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("[AVA OS] Improvement scheduler started")

    def stop(self) -> None:
        """Stop the improvement scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[AVA OS] Improvement scheduler stopped")

    def _run_scheduler(self) -> None:
        """Run the scheduler loop."""
        print("[AVA OS] Improvement loop is monitoring system health")
        print("[AVA OS] Schedule: Daily analysis and autonomous improvements")

        while self.running:
            try:
                # Check if analysis should run
                if self.automation.should_run_loop():
                    print("[AVA OS] Running system health analysis...")
                    analysis = self.automation.analyze_system_health()

                    print(f"[AVA OS] Analysis complete:")
                    print(f"         Healthy: {analysis['healthy_count']}/{analysis['total_frameworks']}")
                    print(f"         Warnings: {analysis['warning_count']}")
                    print(f"         Critical: {analysis['critical_count']}")

                # Check if improvement cycle should run
                if self.improvement_loop.should_run_loop():
                    print("[AVA OS] Running improvement cycle...")
                    result = self.improvement_loop.run_improvement_cycle()

                    if result['status'] == 'completed':
                        print(f"[AVA OS] Improvements applied: {result['improvements_applied']}")
                        print(f"[AVA OS] Successful: {result['improvements_successful']}")
                        if result['improvements_failed'] > 0:
                            print(f"[AVA OS] Failed: {result['improvements_failed']}")

                # Sleep for 1 hour before checking again
                time.sleep(3600)

            except Exception as e:
                print(f"[AVA OS] Improvement scheduler error: {e}")
                time.sleep(300)  # Retry after 5 minutes on error

    def get_status(self) -> dict:
        """Get current scheduler status."""
        return {
            'running': self.running,
            'loop_enabled': self.improvement_loop.config['loop_enabled'],
            'auto_apply_improvements': self.improvement_loop.config['auto_apply_improvements'],
            'total_improvements_run': self.improvement_loop.config['total_improvements_run'],
            'successful': self.improvement_loop.config['successful_improvements'],
            'failed': self.improvement_loop.config['failed_improvements'],
            'last_run': self.improvement_loop.config.get('last_loop_run'),
        }

    def force_improvement_cycle(self) -> dict:
        """Force an immediate improvement cycle (for testing/urgent fixes)."""
        print("[AVA OS] Forcing immediate improvement cycle...")
        result = self.improvement_loop.run_improvement_cycle()
        print(f"[AVA OS] Improvement cycle result: {result['status']}")
        return result


# Global scheduler instance
_scheduler: Optional[ImprovementScheduler] = None


def initialize_scheduler(memory_dir: Path) -> ImprovementScheduler:
    """Initialize the global improvement scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = ImprovementScheduler(memory_dir, run_in_background=True)
    return _scheduler


def get_scheduler() -> Optional[ImprovementScheduler]:
    """Get the global improvement scheduler."""
    return _scheduler
