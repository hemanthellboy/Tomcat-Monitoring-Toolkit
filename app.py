"""
Flask web UI for Tomcat Monitoring Toolkit.
"""
import logging
from flask import Flask, render_template, jsonify
from monitor import MonitoringCoordinator
from config_manager import load_config

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global coordinator instance
coordinator = None


def init_app(config_path: str = 'config.yaml'):
    """
    Initialize the Flask application with monitoring.
    
    Args:
        config_path: Path to configuration file
    """
    global coordinator
    
    # Load configuration
    config = load_config(config_path)
    
    # Initialize coordinator
    coordinator = MonitoringCoordinator(config)
    
    # Start monitoring
    monitoring_config = config['monitoring']
    interval = monitoring_config.get('thread_dump_interval', 30)
    coordinator.start_monitoring(interval=interval)
    
    logger.info("Flask app initialized")


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/alerts')
def alerts_page():
    """Alerts page."""
    return render_template('alerts.html')


@app.route('/metrics')
def metrics_page():
    """Detailed metrics page."""
    return render_template('metrics.html')


@app.route('/api/status')
def api_status():
    """API endpoint for current status."""
    if coordinator is None:
        return jsonify({'error': 'Coordinator not initialized'}), 500
    
    try:
        status = coordinator.get_current_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics')
def api_metrics():
    """API endpoint for current metrics."""
    if coordinator is None:
        return jsonify({'error': 'Coordinator not initialized'}), 500
    
    try:
        metrics = coordinator.current_metrics
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def api_health():
    """API endpoint for health score."""
    if coordinator is None:
        return jsonify({'error': 'Coordinator not initialized'}), 500
    
    try:
        health = coordinator.current_health
        return jsonify(health)
    except Exception as e:
        logger.error(f"Error getting health: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts')
def api_alerts():
    """API endpoint for active alerts."""
    if coordinator is None:
        return jsonify({'error': 'Coordinator not initialized'}), 500
    
    try:
        alerts = coordinator.alert_manager.get_active_alerts()
        return jsonify({
            'alerts': [
                {
                    'level': a.level.value,
                    'title': a.title,
                    'message': a.message,
                    'metric': a.metric,
                    'value': str(a.value),
                    'threshold': str(a.threshold),
                    'timestamp': a.timestamp
                }
                for a in alerts
            ]
        })
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/heap_trend')
def api_heap_trend():
    """API endpoint for heap trend data."""
    if coordinator is None:
        return jsonify({'error': 'Coordinator not initialized'}), 500
    
    try:
        heap_history = coordinator.jmx_monitor.heap_history
        
        # Convert to JSON-serializable format
        trend_data = [
            {
                'timestamp': h.timestamp,
                'used_mb': h.used / (1024 * 1024),
                'max_mb': h.max / (1024 * 1024),
                'usage_percent': h.usage_percent * 100
            }
            for h in heap_history
        ]
        
        return jsonify({'data': trend_data})
    except Exception as e:
        logger.error(f"Error getting heap trend: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/slow_requests')
def api_slow_requests():
    """API endpoint for slow requests."""
    if coordinator is None:
        return jsonify({'error': 'Coordinator not initialized'}), 500
    
    try:
        slow_requests = coordinator.log_parser.get_slow_requests(limit=50)
        
        return jsonify({
            'requests': [
                {
                    'timestamp': r.timestamp.isoformat(),
                    'path': r.path,
                    'method': r.method,
                    'status_code': r.status_code,
                    'response_time_ms': r.response_time_ms,
                    'client_ip': r.client_ip
                }
                for r in slow_requests
            ]
        })
    except Exception as e:
        logger.error(f"Error getting slow requests: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize app
    init_app()
    
    # Run Flask
    ui_config = coordinator.config['ui']
    app.run(
        host=ui_config.get('host', '0.0.0.0'),
        port=ui_config.get('port', 5000),
        debug=ui_config.get('debug', False)
    )
