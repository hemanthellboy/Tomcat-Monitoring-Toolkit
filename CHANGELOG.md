# Changelog

All notable changes to the Tomcat Monitoring Toolkit project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-28

### Added
- **JVM Thread Analysis**: Real-time detection of stuck and BLOCKED threads via thread dumps
- **Heap & Memory Tracking**: Comprehensive heap usage monitoring with OldGen trend analysis
- **OOM Prediction**: Predictive analytics for Out-of-Memory events based on heap growth trends
- **Thread Pool Saturation Monitoring**: Track Tomcat thread pool utilization against capacity
- **Slow Request Correlation**: Parse access logs to identify and correlate slow requests with system issues
- **OS Metrics Collection**: CPU, memory, disk, and system metrics via psutil
- **Health Scoring System**: Weighted health scoring (0-100) with component-level breakdowns
- **Multi-Channel Alerting**: Email (SMTP) and webhook integrations
- **Smart Alert Throttling**: Configurable throttling to prevent alert fatigue
- **Real-time Web Dashboard**: Flask-based UI with auto-refresh capabilities
- **Docker Support**: Complete Docker and docker-compose setup with health checks
- **Security Features**: Non-root execution, configuration validation, YAML-based config management
- **Comprehensive Documentation**: README, testing guide, Docker usage guide, and inline code documentation
- **Health Check Endpoints**: Built-in endpoints for container orchestrators

### Features
- Production-ready monitoring toolkit for Apache Tomcat
- Modular architecture for easy maintenance and extension
- Fail-fast configuration validation with detailed error messages
- Configurable monitoring thresholds and alert parameters
- Real-time metrics collection and analysis
- Historical trend analysis for predictive alerting

### Fixed
- Initial release - no previous version

### Security
- Non-root container execution
- Secure configuration management
- Input validation for all configuration parameters
- TLS support for SMTP email alerts

## [Unreleased]

### Planned Features
- Kubernetes integration and Prometheus metrics export
- Machine learning-based anomaly detection
- Historical metrics storage and advanced analytics
- Multi-Tomcat instance correlation
- Advanced visualization and reporting
- Mobile app for alerts
- LDAP/OAuth integration for UI authentication

---

## How to Upgrade

### From No Previous Version to 1.0.0

1. Clone the repository or download the latest release
2. Configure `config.yaml` for your environment
3. Deploy using Docker Compose or local Python environment
4. Access the dashboard at `http://localhost:5000`

## Support

For issues, questions, or feature requests, please visit:
- [GitHub Issues](https://github.com/yourusername/Tomcat-Monitoring-Toolkit/issues)
- [GitHub Discussions](https://github.com/yourusername/Tomcat-Monitoring-Toolkit/discussions)
