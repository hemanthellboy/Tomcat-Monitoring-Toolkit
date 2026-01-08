"""
Alert delivery mechanisms (email and webhook).
"""
import logging
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from health_scorer import Alert, AlertLevel

logger = logging.getLogger(__name__)


class EmailAlerter:
    """Send alerts via email."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email alerter.
        
        Args:
            config: Email configuration
        """
        self.enabled = config.get('enabled', False)
        self.smtp_host = config.get('smtp_host', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_user = config.get('smtp_user', '')
        self.smtp_password = config.get('smtp_password', '')
        self.from_addr = config.get('from_addr', 'noreply@example.com')
        self.to_addrs = config.get('to_addrs', [])
        self.use_tls = config.get('use_tls', True)
        
        if self.enabled:
            logger.info(f"Email alerter initialized (SMTP: {self.smtp_host}:{self.smtp_port})")
        else:
            logger.info("Email alerter disabled")
    
    def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert via email.
        
        Args:
            alert: Alert object
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Email alerter is disabled")
            return False
        
        if not self.to_addrs:
            logger.warning("No recipient email addresses configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.title}"
            msg['From'] = self.from_addr
            msg['To'] = ', '.join(self.to_addrs)
            
            # Create HTML and plain text versions
            text_body = f"""
Tomcat Monitoring Alert

Level: {alert.level.value.upper()}
Title: {alert.title}
Message: {alert.message}
Metric: {alert.metric}
Current Value: {alert.value}
Threshold: {alert.threshold}
Time: {alert.timestamp}

---
Tomcat Monitoring Toolkit
"""
            
            html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .alert {{ padding: 20px; border-radius: 5px; margin: 10px 0; }}
        .critical {{ background-color: #ffebee; border-left: 5px solid #f44336; }}
        .warning {{ background-color: #fff3e0; border-left: 5px solid #ff9800; }}
        .info {{ background-color: #e3f2fd; border-left: 5px solid #2196f3; }}
        .metric {{ margin: 10px 0; padding: 10px; background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h2>Tomcat Monitoring Alert</h2>
    <div class="alert {alert.level.value}">
        <h3>{alert.title}</h3>
        <p><strong>Level:</strong> {alert.level.value.upper()}</p>
        <p><strong>Message:</strong> {alert.message}</p>
        <div class="metric">
            <p><strong>Metric:</strong> {alert.metric}</p>
            <p><strong>Current Value:</strong> {alert.value}</p>
            <p><strong>Threshold:</strong> {alert.threshold}</p>
        </div>
    </div>
    <hr>
    <p><em>Tomcat Monitoring Toolkit</em></p>
</body>
</html>
"""
            
            # Attach parts
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Alert email sent: {alert.title}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def send_alerts(self, alerts: List[Alert]) -> int:
        """
        Send multiple alerts.
        
        Args:
            alerts: List of alerts
        
        Returns:
            Number of alerts sent successfully
        """
        sent_count = 0
        for alert in alerts:
            if self.send_alert(alert):
                sent_count += 1
        return sent_count


class WebhookAlerter:
    """Send alerts via webhook."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize webhook alerter.
        
        Args:
            config: Webhook configuration
        """
        self.enabled = config.get('enabled', False)
        self.url = config.get('url', '')
        self.method = config.get('method', 'POST').upper()
        self.headers = config.get('headers', {'Content-Type': 'application/json'})
        self.timeout = config.get('timeout', 10)
        
        if self.enabled:
            logger.info(f"Webhook alerter initialized (URL: {self.url})")
        else:
            logger.info("Webhook alerter disabled")
    
    def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert via webhook.
        
        Args:
            alert: Alert object
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Webhook alerter is disabled")
            return False
        
        if not self.url:
            logger.warning("No webhook URL configured")
            return False
        
        try:
            # Prepare payload
            payload = {
                'level': alert.level.value,
                'title': alert.title,
                'message': alert.message,
                'metric': alert.metric,
                'value': str(alert.value),
                'threshold': str(alert.threshold),
                'timestamp': alert.timestamp
            }
            
            # Send request
            if self.method == 'POST':
                response = requests.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout
                )
            elif self.method == 'PUT':
                response = requests.put(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout
                )
            else:
                logger.error(f"Unsupported HTTP method: {self.method}")
                return False
            
            response.raise_for_status()
            logger.info(f"Alert webhook sent: {alert.title}")
            return True
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending webhook: {e}")
            return False
    
    def send_alerts(self, alerts: List[Alert]) -> int:
        """
        Send multiple alerts.
        
        Args:
            alerts: List of alerts
        
        Returns:
            Number of alerts sent successfully
        """
        sent_count = 0
        for alert in alerts:
            if self.send_alert(alert):
                sent_count += 1
        return sent_count


class AlertDispatcher:
    """Dispatch alerts to configured channels."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize alert dispatcher.
        
        Args:
            config: Alerts configuration
        """
        alerts_config = config.get('alerts', {})
        
        self.email_alerter = EmailAlerter(alerts_config.get('email', {}))
        self.webhook_alerter = WebhookAlerter(alerts_config.get('webhook', {}))
        
        logger.info("Alert dispatcher initialized")
    
    def dispatch_alert(self, alert: Alert) -> Dict[str, bool]:
        """
        Dispatch an alert to all enabled channels.
        
        Args:
            alert: Alert to dispatch
        
        Returns:
            Dictionary with channel names and success status
        """
        results = {
            'email': self.email_alerter.send_alert(alert),
            'webhook': self.webhook_alerter.send_alert(alert)
        }
        return results
    
    def dispatch_alerts(self, alerts: List[Alert]) -> Dict[str, int]:
        """
        Dispatch multiple alerts.
        
        Args:
            alerts: List of alerts to dispatch
        
        Returns:
            Dictionary with channel names and count of successful dispatches
        """
        results = {
            'email': self.email_alerter.send_alerts(alerts),
            'webhook': self.webhook_alerter.send_alerts(alerts)
        }
        return results
