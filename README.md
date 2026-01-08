# Tomcat Monitoring Toolkit v1.0

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

A production-ready monitoring toolkit for Apache Tomcat with real-time health analysis, predictive OOM detection, and comprehensive alerting.

## 🚀 Features

### Core Monitoring
- **JVM Thread Analysis**: Detect stuck/BLOCKED threads via thread dumps with configurable thresholds
- **Heap & Memory Tracking**: Real-time heap usage monitoring with OldGen trend analysis
- **OOM Prediction**: Predictive analytics for Out-of-Memory events based on heap growth trends
- **Thread Pool Saturation**: Monitor Tomcat thread pool utilization and capacity
- **Slow Request Correlation**: Parse access logs to identify and correlate slow requests with system issues
- **OS Metrics**: CPU, memory, disk, and basic system metrics via psutil

### Health & Alerting
- **Health Score**: Weighted health scoring system (0-100) with component breakdowns
- **Multi-Channel Alerts**: Email (SMTP) and webhook integrations
- **Smart Throttling**: Configurable alert throttling to prevent alert fatigue
- **Real-time Dashboard**: Flask-based web UI with auto-refresh

### Production-Ready
- **Non-Root Execution**: Runs as non-privileged user in Docker
- **Fail-Fast Validation**: Configuration validation with detailed error messages
- **YAML Configuration**: Simple, readable configuration management
- **Modular Architecture**: Clean separation of concerns for easy maintenance
- **Docker Support**: Complete Docker and docker-compose setup
- **Health Checks**: Built-in health check endpoints for orchestrators

## 📋 Prerequisites

- Python 3.10+
- Docker & docker-compose (for containerized deployment)
- Tomcat with JMX enabled (for production use)
- Access logs configured in Tomcat

## 🔧 Quick Start

### Using Docker Compose (Recommended)

1. **Clone and configure**:
```bash
git clone <repository-url>
cd Tomcat-Monitoring-Toolkit
cp config.yaml config.yaml.local  # Optional: keep a local copy
```

2. **Edit configuration**:
```bash
# Edit config.yaml to match your environment
vim config.yaml
```

Key settings to update:
- `jmx.host` and `jmx.port`: Your Tomcat JMX endpoint
- `tomcat.access_log_path`: Path to Tomcat access logs
- `alerts.email.*`: SMTP settings (if using email alerts)
- `alerts.webhook.*`: Webhook URL (if using webhook alerts)

3. **Start the monitoring toolkit**:
```bash
docker-compose up -d
```

4. **Access the dashboard**:
```
http://localhost:5000
```

### Local Development Setup

1. **Create virtual environment**:
```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure**:
```bash
cp config.yaml config.local.yaml
# Edit config.local.yaml for your environment
```

4. **Run**:
```bash
python app.py
```

## 📁 Project Structure

```
Tomcat-Monitoring-Toolkit/
├── app.py                  # Flask web application
├── monitor.py              # Main monitoring coordinator
├── config_manager.py       # Configuration management with validation
├── jmx_monitor.py          # JMX-based metrics collection
├── os_monitor.py           # OS-level metrics (psutil)
├── log_parser.py           # Access log parsing and analysis
├── health_scorer.py        # Health scoring and alert management
├── alerter.py              # Alert delivery (email/webhook)
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose orchestration
├── templates/              # Flask HTML templates
│   ├── index.html         # Main dashboard
│   ├── alerts.html        # Alerts page
│   └── metrics.html       # Detailed metrics page
└── README.md              # This file
```

## ⚙️ Configuration

### JMX Setup

To enable JMX on Tomcat, add these JVM options:

```bash
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote"
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote.port=9999"
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote.ssl=false"
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote.authenticate=false"
```

**Security Note**: For production, enable authentication and SSL:
```bash
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote.authenticate=true"
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote.password.file=/path/to/jmxremote.password"
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote.ssl=true"
```

### Access Log Format

Configure Tomcat to include response time in access logs:

```xml
<Valve className="org.apache.catalina.valves.AccessLogValve"
       directory="logs"
       prefix="access_log"
       suffix=".txt"
       pattern="%h %l %u %t &quot;%r&quot; %s %b %D &quot;%{User-Agent}i&quot;" />
```

The `%D` directive logs response time in milliseconds.

### Threshold Configuration

Adjust monitoring thresholds in `config.yaml`:

```yaml
monitoring:
  heap_warn_threshold: 0.7      # 70% heap usage triggers warning
  heap_critical_threshold: 0.85  # 85% heap usage triggers critical alert
  oom_prediction_threshold: 3600 # Alert if OOM predicted within 1 hour
  thread_dump_interval: 30       # Thread dump collection interval (seconds)
```

## 📊 Web UI

### Dashboard (`/`)
- Overall health score (0-100)
- Real-time metrics visualization
- Connection status
- Active alerts summary
- Heap usage trend chart

### Alerts (`/alerts`)
- Active alerts by severity
- Alert details with timestamps
- Alert history

### Metrics (`/metrics`)
- Detailed JVM metrics
- System resource utilization
- Slow request analysis
- Raw JSON metrics view

## 🔔 Alerting

### Email Alerts

Configure SMTP in `config.yaml`:

```yaml
alerts:
  enabled: true
  email:
    enabled: true
    smtp_host: smtp.gmail.com
    smtp_port: 587
    smtp_user: your-email@example.com
    smtp_password: your-app-password
    from_addr: tomcat-monitor@example.com
    to_addrs:
      - ops-team@example.com
    use_tls: true
```

### Webhook Alerts

Configure webhook in `config.yaml`:

```yaml
alerts:
  webhook:
    enabled: true
    url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
    method: POST
    headers:
      Content-Type: application/json
    timeout: 10
```

### Alert Types

- **Critical Heap Usage**: Heap exceeds critical threshold
- **High OldGen Usage**: Old Generation memory pressure
- **OOM Prediction**: Out-of-Memory predicted within threshold
- **Stuck Threads**: Threads blocked for extended periods
- **Thread Pool Saturation**: Thread pool near/at capacity
- **High CPU/Memory**: System resource exhaustion

## 🔒 Security

### Non-Root Execution

The Docker container runs as a non-root user (`tomcat-monitor`):

```dockerfile
RUN groupadd -r tomcat-monitor && useradd -r -g tomcat-monitor tomcat-monitor
USER tomcat-monitor
```

### Read-Only JMX

JMX access is read-only by design. The toolkit does not invoke any management operations.

### Configuration Validation

All configuration is validated at startup with fail-fast behavior:

```python
# Validates thresholds, required fields, data types
config = load_config('config.yaml')  # Exits with error if invalid
```

## 🚢 Deployment

### Docker

Build and run:
```bash
docker build -t tomcat-monitor:latest .
docker run -d -p 5000:5000 --name tomcat-monitor tomcat-monitor:latest
```

### Docker Compose

Production deployment:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f tomcat-monitor
```

Stop:
```bash
docker-compose down
```

### Kubernetes

Example deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tomcat-monitor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tomcat-monitor
  template:
    metadata:
      labels:
        app: tomcat-monitor
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
      - name: tomcat-monitor
        image: tomcat-monitor:latest
        ports:
        - containerPort: 5000
        volumeMounts:
        - name: config
          mountPath: /app/config.yaml
          subPath: config.yaml
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: config
        configMap:
          name: tomcat-monitor-config
```

## 📈 API Endpoints

- `GET /api/status` - Current system status with all metrics
- `GET /api/metrics` - Raw metrics data
- `GET /api/health` - Health score
- `GET /api/alerts` - Active alerts
- `GET /api/heap_trend` - Heap usage trend data
- `GET /api/slow_requests` - Recent slow requests

## 🧪 Testing

Test configuration validation:
```bash
python -c "from config_manager import load_config; config = load_config('config.yaml'); print('Config valid!')"
```

Test individual components:
```bash
# Test OS monitoring
python -c "from os_monitor import OSMonitor; m = OSMonitor(); print(m.get_all_metrics())"

# Test log parsing (update path)
python -c "from log_parser import AccessLogParser; p = AccessLogParser('/path/to/access.log'); print(p.get_request_stats())"
```

## 🐛 Troubleshooting

### JMX Connection Issues

**Symptom**: "JMX port not reachable"

**Solutions**:
1. Verify JMX is enabled on Tomcat
2. Check firewall rules
3. Ensure correct host/port in config.yaml
4. Test connectivity: `telnet <host> <port>`

### Access Log Parsing Fails

**Symptom**: "Failed to parse access logs"

**Solutions**:
1. Verify access log path in config.yaml
2. Check log format matches expected pattern
3. Ensure read permissions on log file
4. Review log pattern in log_parser.py

### High Memory Usage

**Symptom**: Monitor consuming too much memory

**Solutions**:
1. Reduce history retention in config
2. Decrease monitoring frequency
3. Limit access log tail size

### Alerts Not Sending

**Symptom**: No email/webhook alerts received

**Solutions**:
1. Verify `alerts.enabled: true` in config.yaml
2. Check SMTP/webhook credentials
3. Review application logs for errors
4. Test connectivity to SMTP/webhook server

## 📝 Logging

Logs are written to:
- Console (stdout/stderr)
- `/var/log/tomcat-monitor/monitor.log` (in Docker)

Log level can be configured in `config.yaml`:
```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Apache Tomcat team
- Python psutil developers
- Flask framework
- Chart.js for visualizations

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**DevOps Tips**:
- Monitor the monitor: Use external health checks on the `/api/health` endpoint
- Resource limits: Set memory/CPU limits in docker-compose or k8s
- Log aggregation: Forward logs to your centralized logging system
- Metrics export: Consider adding Prometheus exporter for integration with existing monitoring
- Backup config: Keep `config.yaml` in version control (without secrets)
- Secrets management: Use environment variables or secret management tools for sensitive data

**Production Checklist**:
- [ ] JMX authentication enabled
- [ ] SMTP credentials secured
- [ ] Non-root user configured
- [ ] Log rotation enabled
- [ ] Health check endpoint monitored
- [ ] Alert throttling configured
- [ ] Resource limits set
- [ ] Backup/HA strategy defined