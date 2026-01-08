"""
Health scoring and alerting system.
"""
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert object."""
    level: AlertLevel
    title: str
    message: str
    metric: str
    value: Any
    threshold: Any
    timestamp: float


class HealthScorer:
    """
    Calculate health score based on multiple metrics.
    
    Health score ranges from 0-100 where:
    - 90-100: Healthy (green)
    - 70-89: Warning (yellow)
    - 0-69: Critical (red)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize health scorer.
        
        Args:
            config: Configuration dictionary with weights and thresholds
        """
        self.config = config
        
        # Get weights
        health_config = config.get('health_score', {})
        self.heap_weight = health_config.get('heap_weight', 0.25)
        self.thread_pool_weight = health_config.get('thread_pool_weight', 0.25)
        self.cpu_weight = health_config.get('cpu_weight', 0.20)
        self.memory_weight = health_config.get('memory_weight', 0.15)
        self.stuck_threads_weight = health_config.get('stuck_threads_weight', 0.15)
        
        # Get thresholds
        monitoring = config.get('monitoring', {})
        self.heap_warn = monitoring.get('heap_warn_threshold', 0.7)
        self.heap_critical = monitoring.get('heap_critical_threshold', 0.85)
        self.thread_pool_warn = config.get('tomcat', {}).get('thread_pool_warn_threshold', 0.7)
        self.thread_pool_critical = config.get('tomcat', {}).get('thread_pool_critical_threshold', 0.9)
        self.cpu_warn = monitoring.get('cpu_warn_threshold', 0.8)
        self.cpu_critical = monitoring.get('cpu_critical_threshold', 0.95)
        self.memory_warn = monitoring.get('memory_warn_threshold', 0.8)
        self.memory_critical = monitoring.get('memory_critical_threshold', 0.9)
        
        logger.info("Health scorer initialized")
    
    def _score_metric(self, value: float, warn_threshold: float, critical_threshold: float) -> float:
        """
        Score a single metric (0-100).
        
        Args:
            value: Current metric value (0-1 normalized)
            warn_threshold: Warning threshold
            critical_threshold: Critical threshold
        
        Returns:
            Score from 0-100
        """
        if value <= warn_threshold:
            # Healthy range: linear from 100 at 0% to 90 at warn threshold
            return 100 - (value / warn_threshold) * 10
        elif value <= critical_threshold:
            # Warning range: linear from 90 at warn to 70 at critical
            range_size = critical_threshold - warn_threshold
            position = (value - warn_threshold) / range_size
            return 90 - (position * 20)
        else:
            # Critical range: exponential decay from 70 at critical to 0 at 100%
            range_size = 1.0 - critical_threshold
            position = (value - critical_threshold) / range_size
            return max(0, 70 * (1 - position))
    
    def calculate_health_score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall health score.
        
        Args:
            metrics: Dictionary containing all metrics
        
        Returns:
            Dictionary with overall score and component scores
        """
        scores = {}
        
        # Heap score
        heap_usage = metrics.get('heap', {}).get('usage_percent', 0)
        scores['heap'] = self._score_metric(heap_usage, self.heap_warn, self.heap_critical)
        
        # Thread pool score
        thread_pool_util = metrics.get('thread_pool', {}).get('utilization', 0)
        scores['thread_pool'] = self._score_metric(
            thread_pool_util,
            self.thread_pool_warn,
            self.thread_pool_critical
        )
        
        # CPU score
        cpu_usage = metrics.get('os', {}).get('cpu', {}).get('cpu_percent', 0) / 100
        scores['cpu'] = self._score_metric(cpu_usage, self.cpu_warn, self.cpu_critical)
        
        # Memory score
        memory_usage = metrics.get('os', {}).get('memory', {}).get('percent', 0) / 100
        scores['memory'] = self._score_metric(memory_usage, self.memory_warn, self.memory_critical)
        
        # Stuck threads score (inverted - more stuck threads = lower score)
        stuck_threads = metrics.get('stuck_threads', 0)
        if stuck_threads == 0:
            scores['stuck_threads'] = 100
        elif stuck_threads < 5:
            scores['stuck_threads'] = 80
        elif stuck_threads < 10:
            scores['stuck_threads'] = 50
        else:
            scores['stuck_threads'] = 0
        
        # Calculate weighted overall score
        overall_score = (
            scores['heap'] * self.heap_weight +
            scores['thread_pool'] * self.thread_pool_weight +
            scores['cpu'] * self.cpu_weight +
            scores['memory'] * self.memory_weight +
            scores['stuck_threads'] * self.stuck_threads_weight
        )
        
        return {
            'overall_score': round(overall_score, 2),
            'component_scores': scores,
            'health_status': self._get_health_status(overall_score),
            'timestamp': time.time()
        }
    
    def _get_health_status(self, score: float) -> str:
        """Get health status from score."""
        if score >= 90:
            return 'healthy'
        elif score >= 70:
            return 'warning'
        else:
            return 'critical'


class AlertManager:
    """
    Manage alerts and alert throttling.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize alert manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.alerts = []
        self.alert_history = []
        
        # Alert throttling
        self.throttle_minutes = config.get('alerts', {}).get('throttle_minutes', 15)
        self.last_alert_times = {}
        
        logger.info("Alert manager initialized")
    
    def check_metrics_for_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """
        Check metrics and generate alerts.
        
        Args:
            metrics: Dictionary containing all metrics
        
        Returns:
            List of new alerts
        """
        new_alerts = []
        monitoring = self.config.get('monitoring', {})
        tomcat = self.config.get('tomcat', {})
        
        # Check heap usage
        heap_usage = metrics.get('heap', {}).get('usage_percent', 0)
        if heap_usage >= monitoring.get('heap_critical_threshold', 0.85):
            alert = Alert(
                level=AlertLevel.CRITICAL,
                title="Critical Heap Usage",
                message=f"Heap usage is at {heap_usage*100:.1f}%",
                metric="heap_usage",
                value=heap_usage,
                threshold=monitoring.get('heap_critical_threshold'),
                timestamp=time.time()
            )
            new_alerts.append(alert)
        elif heap_usage >= monitoring.get('heap_warn_threshold', 0.7):
            alert = Alert(
                level=AlertLevel.WARNING,
                title="High Heap Usage",
                message=f"Heap usage is at {heap_usage*100:.1f}%",
                metric="heap_usage",
                value=heap_usage,
                threshold=monitoring.get('heap_warn_threshold'),
                timestamp=time.time()
            )
            new_alerts.append(alert)
        
        # Check OldGen usage
        oldgen_usage = metrics.get('oldgen', {}).get('usage_percent', 0)
        if oldgen_usage >= monitoring.get('oldgen_critical_threshold', 0.9):
            alert = Alert(
                level=AlertLevel.CRITICAL,
                title="Critical OldGen Usage",
                message=f"OldGen usage is at {oldgen_usage*100:.1f}%",
                metric="oldgen_usage",
                value=oldgen_usage,
                threshold=monitoring.get('oldgen_critical_threshold'),
                timestamp=time.time()
            )
            new_alerts.append(alert)
        
        # Check OOM prediction
        oom_prediction = metrics.get('oom_prediction')
        if oom_prediction and oom_prediction.get('predicted'):
            time_to_oom = oom_prediction.get('time_to_oom_seconds', 0)
            threshold = monitoring.get('oom_prediction_threshold', 3600)
            
            if time_to_oom < threshold:
                alert = Alert(
                    level=AlertLevel.CRITICAL,
                    title="OOM Predicted",
                    message=f"OOM predicted in {time_to_oom/60:.1f} minutes",
                    metric="oom_prediction",
                    value=time_to_oom,
                    threshold=threshold,
                    timestamp=time.time()
                )
                new_alerts.append(alert)
        
        # Check stuck threads
        stuck_threads = metrics.get('stuck_threads', 0)
        if stuck_threads > 0:
            level = AlertLevel.CRITICAL if stuck_threads >= 10 else AlertLevel.WARNING
            alert = Alert(
                level=level,
                title=f"Stuck Threads Detected",
                message=f"{stuck_threads} threads are stuck or blocked",
                metric="stuck_threads",
                value=stuck_threads,
                threshold=0,
                timestamp=time.time()
            )
            new_alerts.append(alert)
        
        # Check thread pool saturation
        thread_pool_util = metrics.get('thread_pool', {}).get('utilization', 0)
        if thread_pool_util >= tomcat.get('thread_pool_critical_threshold', 0.9):
            alert = Alert(
                level=AlertLevel.CRITICAL,
                title="Critical Thread Pool Saturation",
                message=f"Thread pool utilization is at {thread_pool_util*100:.1f}%",
                metric="thread_pool_utilization",
                value=thread_pool_util,
                threshold=tomcat.get('thread_pool_critical_threshold'),
                timestamp=time.time()
            )
            new_alerts.append(alert)
        elif thread_pool_util >= tomcat.get('thread_pool_warn_threshold', 0.7):
            alert = Alert(
                level=AlertLevel.WARNING,
                title="High Thread Pool Utilization",
                message=f"Thread pool utilization is at {thread_pool_util*100:.1f}%",
                metric="thread_pool_utilization",
                value=thread_pool_util,
                threshold=tomcat.get('thread_pool_warn_threshold'),
                timestamp=time.time()
            )
            new_alerts.append(alert)
        
        # Check CPU
        cpu_percent = metrics.get('os', {}).get('cpu', {}).get('cpu_percent', 0) / 100
        if cpu_percent >= monitoring.get('cpu_critical_threshold', 0.95):
            alert = Alert(
                level=AlertLevel.CRITICAL,
                title="Critical CPU Usage",
                message=f"CPU usage is at {cpu_percent*100:.1f}%",
                metric="cpu_usage",
                value=cpu_percent,
                threshold=monitoring.get('cpu_critical_threshold'),
                timestamp=time.time()
            )
            new_alerts.append(alert)
        
        # Check memory
        memory_percent = metrics.get('os', {}).get('memory', {}).get('percent', 0) / 100
        if memory_percent >= monitoring.get('memory_critical_threshold', 0.9):
            alert = Alert(
                level=AlertLevel.CRITICAL,
                title="Critical Memory Usage",
                message=f"Memory usage is at {memory_percent*100:.1f}%",
                metric="memory_usage",
                value=memory_percent,
                threshold=monitoring.get('memory_critical_threshold'),
                timestamp=time.time()
            )
            new_alerts.append(alert)
        
        # Filter throttled alerts
        filtered_alerts = []
        for alert in new_alerts:
            if self._should_send_alert(alert):
                filtered_alerts.append(alert)
                self.alerts.append(alert)
                self.alert_history.append(alert)
                self.last_alert_times[alert.metric] = alert.timestamp
        
        return filtered_alerts
    
    def _should_send_alert(self, alert: Alert) -> bool:
        """Check if alert should be sent based on throttling."""
        last_time = self.last_alert_times.get(alert.metric)
        
        if last_time is None:
            return True
        
        time_since_last = alert.timestamp - last_time
        return time_since_last >= (self.throttle_minutes * 60)
    
    def get_active_alerts(self, max_age_seconds: int = 300) -> List[Alert]:
        """Get alerts from the last N seconds."""
        cutoff = time.time() - max_age_seconds
        return [a for a in self.alerts if a.timestamp > cutoff]
    
    def clear_old_alerts(self, max_age_seconds: int = 3600):
        """Clear alerts older than max_age_seconds."""
        cutoff = time.time() - max_age_seconds
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff]
