"""
Main monitoring coordinator that orchestrates all monitoring components.
"""
import logging
import time
import threading
from typing import Dict, Any, Optional
from config_manager import Config
from jmx_monitor import JMXMonitor
from os_monitor import OSMonitor
from log_parser import AccessLogParser
from health_scorer import HealthScorer, AlertManager
from alerter import AlertDispatcher

logger = logging.getLogger(__name__)


class MonitoringCoordinator:
    """
    Coordinates all monitoring activities.
    
    This is the main orchestrator that:
    - Collects metrics from all sources
    - Calculates health scores
    - Generates alerts
    - Maintains monitoring state
    """
    
    def __init__(self, config: Config):
        """
        Initialize monitoring coordinator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize monitors
        jmx_config = config['jmx']
        self.jmx_monitor = JMXMonitor(
            host=jmx_config['host'],
            port=jmx_config['port'],
            timeout=jmx_config.get('connection_timeout', 10)
        )
        
        self.os_monitor = OSMonitor()
        
        tomcat_config = config['tomcat']
        self.log_parser = AccessLogParser(
            log_path=tomcat_config['access_log_path'],
            slow_threshold_ms=tomcat_config['slow_request_threshold']
        )
        
        # Initialize health and alerting
        self.health_scorer = HealthScorer(config.config)
        self.alert_manager = AlertManager(config.config)
        self.alert_dispatcher = AlertDispatcher(config.config)
        
        # Monitoring state
        self.current_metrics = {}
        self.current_health = {}
        self.running = False
        self.monitor_thread = None
        
        # Try to connect to JMX
        self.jmx_monitor.connect()
        
        logger.info("Monitoring coordinator initialized")
    
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect all metrics from all sources.
        
        Returns:
            Dictionary containing all metrics
        """
        metrics = {}
        
        # JMX metrics
        try:
            jmx_metrics = self.jmx_monitor.get_all_metrics()
            metrics.update(jmx_metrics)
        except Exception as e:
            logger.error(f"Failed to collect JMX metrics: {e}")
            metrics['jmx_error'] = str(e)
        
        # OS metrics
        try:
            os_metrics = self.os_monitor.get_all_metrics()
            metrics['os'] = os_metrics
        except Exception as e:
            logger.error(f"Failed to collect OS metrics: {e}")
            metrics['os_error'] = str(e)
        
        # Access log metrics
        try:
            # Tail recent logs
            self.log_parser.tail_log(num_lines=100)
            request_stats = self.log_parser.get_request_stats()
            metrics['requests'] = request_stats
            metrics['slow_requests'] = len(self.log_parser.get_slow_requests(limit=50))
        except Exception as e:
            logger.error(f"Failed to parse access logs: {e}")
            metrics['log_error'] = str(e)
        
        metrics['collection_timestamp'] = time.time()
        return metrics
    
    def calculate_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate health score from metrics.
        
        Args:
            metrics: Collected metrics
        
        Returns:
            Health score dictionary
        """
        try:
            health = self.health_scorer.calculate_health_score(metrics)
            return health
        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return {
                'overall_score': 0,
                'health_status': 'error',
                'error': str(e)
            }
    
    def check_and_dispatch_alerts(self, metrics: Dict[str, Any]) -> int:
        """
        Check metrics for alerts and dispatch them.
        
        Args:
            metrics: Collected metrics
        
        Returns:
            Number of alerts dispatched
        """
        try:
            # Check for new alerts
            new_alerts = self.alert_manager.check_metrics_for_alerts(metrics)
            
            if new_alerts:
                logger.info(f"Generated {len(new_alerts)} new alerts")
                
                # Dispatch alerts
                results = self.alert_dispatcher.dispatch_alerts(new_alerts)
                total_dispatched = sum(results.values())
                
                logger.info(f"Dispatched alerts: {results}")
                return total_dispatched
            
            return 0
        except Exception as e:
            logger.error(f"Failed to check/dispatch alerts: {e}")
            return 0
    
    def monitoring_loop(self, interval: int = 30):
        """
        Main monitoring loop.
        
        Args:
            interval: Monitoring interval in seconds
        """
        logger.info(f"Starting monitoring loop (interval: {interval}s)")
        
        while self.running:
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                self.current_metrics = metrics
                
                # Calculate health
                health = self.calculate_health(metrics)
                self.current_health = health
                
                # Check for alerts
                self.check_and_dispatch_alerts(metrics)
                
                # Clean up old alerts
                self.alert_manager.clear_old_alerts()
                
                logger.debug(f"Monitoring cycle complete. Health: {health.get('overall_score')}")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Sleep for interval
            time.sleep(interval)
    
    def start_monitoring(self, interval: int = 30):
        """
        Start monitoring in background thread.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.running:
            logger.warning("Monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self.monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info("Monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        if not self.running:
            logger.warning("Monitoring not running")
            return
        
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("Monitoring stopped")
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Get current monitoring status.
        
        Returns:
            Dictionary with current metrics, health, and alerts
        """
        return {
            'metrics': self.current_metrics,
            'health': self.current_health,
            'active_alerts': [
                {
                    'level': a.level.value,
                    'title': a.title,
                    'message': a.message,
                    'metric': a.metric,
                    'value': a.value,
                    'timestamp': a.timestamp
                }
                for a in self.alert_manager.get_active_alerts()
            ],
            'monitoring_active': self.running,
            'jmx_connected': self.jmx_monitor.connected,
            'timestamp': time.time()
        }
