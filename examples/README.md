# Examples

This directory contains ready-to-use configuration and deployment examples for the Tomcat Monitoring Toolkit.

## 📋 Available Examples

### 1. **production-setup.yaml**
A comprehensive production-grade configuration example with detailed comments.

**Features:**
- Recommended thresholds for production environments
- Email and webhook alert configuration
- Security best practices
- Performance optimization guidelines

**Usage:**
```bash
cp production-setup.yaml ../config.yaml
# Edit config.yaml with your environment details
```

### 2. **docker-compose-with-tomcat.yml**
Complete Docker Compose setup with Tomcat server, monitoring toolkit, and optional Prometheus/Grafana.

**Services included:**
- Apache Tomcat 9 with JMX enabled
- Tomcat Monitoring Toolkit
- Prometheus (optional, for metrics collection)
- Grafana (optional, for visualization)

**Features:**
- Automatic JMX configuration
- Health checks for all services
- Persistent volume management
- Network isolation

**Usage:**
```bash
# Start all services
docker-compose -f docker-compose-with-tomcat.yml up -d

# Access services
# Tomcat: http://localhost:8080
# Monitor Dashboard: http://localhost:5000
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)

# View logs
docker-compose -f docker-compose-with-tomcat.yml logs -f

# Stop
docker-compose -f docker-compose-with-tomcat.yml down
```

### 3. **kubernetes-deployment.yaml**
Production-ready Kubernetes deployment manifests with best practices.

**Includes:**
- ConfigMap for configuration management
- ServiceAccount with minimal RBAC permissions
- High-availability deployment with 2+ replicas
- Resource limits and requests
- Liveness and readiness probes
- Security context (non-root user)
- Horizontal Pod Autoscaler
- Ingress configuration with TLS
- Network policies

**Features:**
- Automatic rollback on deployment failure
- Pod anti-affinity for distribution
- Auto-scaling based on CPU/memory
- Health monitoring integration
- Secrets management support

**Usage:**
```bash
# Create namespace
kubectl create namespace monitoring

# Apply manifests
kubectl apply -f kubernetes-deployment.yaml

# Check deployment status
kubectl get deployment -n monitoring
kubectl get pods -n monitoring

# View logs
kubectl logs -f deployment/tomcat-monitor -n monitoring

# Port forward for local access
kubectl port-forward -n monitoring svc/tomcat-monitor 5000:5000

# Access dashboard
# http://localhost:5000
# Or via ingress: https://tomcat-monitor.example.com

# Update configuration
kubectl set env deployment/tomcat-monitor -n monitoring LOG_LEVEL=DEBUG

# Scale manually
kubectl scale deployment tomcat-monitor --replicas=3 -n monitoring
```

## 🔧 Customization

### For Your Environment

1. **Docker Compose**:
   - Update Tomcat version if needed
   - Modify port mappings
   - Adjust volume paths
   - Configure environment variables

2. **Kubernetes**:
   - Update image repository/tag
   - Modify resource limits based on your cluster
   - Update ingress hostname
   - Configure RBAC permissions as needed
   - Set up certificate issuer for TLS

3. **Configuration (YAML)**:
   - Adjust thresholds based on your baseline
   - Configure email/webhook endpoints
   - Set alert throttling intervals
   - Customize health score weights

## 🚀 Quick Start

### Option 1: Docker Compose (Easiest)
```bash
cd examples
docker-compose -f docker-compose-with-tomcat.yml up -d
# Access at http://localhost:5000
```

### Option 2: Kubernetes (Recommended for Production)
```bash
kubectl apply -f kubernetes-deployment.yaml
kubectl port-forward -n monitoring svc/tomcat-monitor 5000:5000
# Access at http://localhost:5000
```

### Option 3: Manual Configuration
```bash
cp production-setup.yaml ../config.yaml
# Edit config.yaml
python app.py
# Access at http://localhost:5000
```

## 📊 Architecture

### Docker Compose Architecture
```
┌────────────────────────────────────┐
│     Tomcat Application Server      │
│  (Port 8080, JMX on 9999)          │
└────────────────────────────────────┘
            ↓ JMX Connection
┌────────────────────────────────────┐
│  Tomcat Monitoring Toolkit         │
│  (Port 5000 Dashboard)             │
├────────────────────────────────────┤
│ - Real-time Monitoring             │
│ - Health Scoring                   │
│ - Alert Management                 │
└────────────────────────────────────┘
       ↓ Metrics                 ↓ Alerts
┌──────────────┐           ┌──────────────┐
│ Prometheus   │           │ Email/Webhook│
│ (9090)       │           │ Integrations │
└──────────────┘           └──────────────┘
       ↓ Metrics
┌──────────────┐
│ Grafana      │
│ (3000)       │
└──────────────┘
```

### Kubernetes Architecture
```
┌─────────────────────────────────────────────┐
│          Kubernetes Cluster                 │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─ Monitoring Namespace ────────────────┐  │
│  │                                       │  │
│  │  Pod 1: tomcat-monitor (Primary)     │  │
│  │  Pod 2: tomcat-monitor (HA)          │  │
│  │  Service: tomcat-monitor-svc         │  │
│  │  ConfigMap: tomcat-monitor-config    │  │
│  │  HPA: Auto-scaling (2-5 replicas)    │  │
│  │                                       │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌─ Ingress (TLS) ────────────────────────┐ │
│  │ tomcat-monitor.example.com             │ │
│  └───────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

## ⚠️ Important Notes

1. **Secrets Management**:
   - Never commit sensitive data to version control
   - Use environment variables or Kubernetes secrets
   - Rotate credentials regularly

2. **Security**:
   - Always enable JMX authentication in production
   - Use HTTPS/TLS for web dashboard
   - Implement network policies in Kubernetes
   - Run as non-root user (already configured)

3. **Performance**:
   - Adjust `thread_dump_interval` based on overhead
   - Set appropriate resource limits
   - Monitor the monitor's own resource usage
   - Use log rotation to prevent disk space issues

4. **High Availability**:
   - Deploy multiple instances behind a load balancer
   - Use persistent volumes for logs
   - Implement backup and recovery procedures
   - Monitor all instances independently

## 📖 Additional Resources

- [Main README](../README.md) - Project overview
- [TESTING.md](../TESTING.md) - Testing guide
- [DOCKER_USAGE.md](../DOCKER_USAGE.md) - Docker details
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contributing guidelines

## 🆘 Support

For issues or questions about these examples:
1. Check the main README troubleshooting section
2. Review GitHub issues
3. Create a new issue with details about your setup

---

**Happy monitoring! 🚀**
