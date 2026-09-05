# Production Operations Guide

## Overview

PromptEasyAI Phase 13 deployment provides comprehensive infrastructure for production deployments including secrets management, HTTPS support, monitoring, quotas, and security validation.

## Deployment Scenarios

### Scenario 1: Local Development

```bash
# Set environment to development
export PROMPTEASY_ENV=development
export PROMPTEASY_PROVIDER=offline

# Run service
python -m uvicorn prompteasy.service:app --reload
```

### Scenario 2: Docker Compose (Staging/Testing)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  prompteasy:
    build: .
    ports:
      - "8000:8000"
    environment:
      PROMPTEASY_ENV: staging
      PROMPTEASY_PROVIDER: offline
      PROMPTEASY_STORAGE_PATH: /var/lib/prompteasy/prompteasy.db
      PROMPTEASY_LOG_LEVEL: DEBUG
    volumes:
      - prompteasy_data:/var/lib/prompteasy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  prompteasy_data:
```

Run with:
```bash
docker-compose up -d
```

### Scenario 3: Kubernetes Production Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prompteasyai
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: prompteasyai
  template:
    metadata:
      labels:
        app: prompteasyai
    spec:
      containers:
      - name: prompteasyai
        image: prompteasyai:0.1.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: PROMPTEASY_ENV
          value: "production"
        - name: PROMPTEASY_PROVIDER
          value: "groq"
        - name: PROMPTEASY_LOG_LEVEL
          value: "INFO"
        - name: PROMPTEASY_RATE_LIMIT
          value: "100"
        - name: PROMPTEASY_STORAGE_PATH
          value: "/var/lib/prompteasy/prompteasy.db"
        envFrom:
        - secretRef:
            name: prompteasy-secrets
        volumeMounts:
        - name: storage
          mountPath: /var/lib/prompteasy
        - name: certificates
          mountPath: /etc/ssl
          readOnly: true
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: prompteasy-storage
      - name: certificates
        secret:
          secretName: prompteasy-tls
          defaultMode: 0400
---
apiVersion: v1
kind: Service
metadata:
  name: prompteasyai
  namespace: production
spec:
  type: LoadBalancer
  selector:
    app: prompteasyai
  ports:
  - port: 443
    targetPort: 8000
    protocol: TCP
---
apiVersion: v1
kind: Secret
metadata:
  name: prompteasy-secrets
  namespace: production
type: Opaque
stringData:
  PROMPTEASY_GROQ_API_KEY: "your-api-key"
  PROMPTEASY_AUTH_TOKEN: "your-auth-token"
  PROMPTEASY_JWT_SECRET: "your-jwt-secret-min-32-chars"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prompteasy-storage
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

Deploy with:
```bash
kubectl apply -f deployment.yaml
kubectl get pod -n production
kubectl logs -n production deployment/prompteasyai
```

## Monitoring and Observability

### Health Checks

Monitor service health:

```bash
# Local health check
curl -v http://localhost:8000/health

# Expected response (healthy)
{
  "status": "ok",
  "service": "prompteasyai",
  "version": "0.1.0",
  "environment": "production",
  "deployment_health": {
    "healthy": true,
    "checks": {
      "environment": "production",
      "storage": {"healthy": true, ...},
      "secrets": {"healthy": true, ...},
      "https": {"healthy": true, ...},
      "quotas": {"healthy": true, ...}
    }
  }
}
```

### Metrics and Monitoring

Access metrics:

```bash
curl http://localhost:8000/api/metrics | jq .
```

Set up monitoring with Prometheus:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prompteasyai'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/metrics'
```

### Logging

Configure log aggregation (ELK Stack example):

```bash
# Logs are written to stdout in JSON format in production
# Capture and send to ELK:
docker logs container-name | jq . | logstash-input-stdin
```

## Maintenance Tasks

### Database Backup

```bash
# Manual backup
python -m prompteasy.cli storage --backup backups/prompteasy-$(date +%Y%m%d).db

# Automated daily backup (cron)
0 2 * * * /path/to/venv/bin/python -m prompteasy.cli storage --backup /backups/prompteasy-$(date +\%Y\%m\%d).db
```

### Database Restore

```bash
# List available backups
ls -la backups/

# Restore from backup
python -m prompteasy.cli storage --restore backups/prompteasy-20240905.db

# Verify restore
curl http://localhost:8000/api/history -H "Authorization: Bearer user.token"
```

## Security Operations

### Regular Security Checks

```bash
# Daily vulnerability scan
python -c "
from prompteasy.performance import VulnerabilityScanner
import json
report = VulnerabilityScanner.generate_security_report()
if report['summary']['critical_issues'] > 0:
    # Alert team
    print('CRITICAL SECURITY ISSUES FOUND')
else:
    print('Security check PASSED')
"

# Weekly dependency audit
pip audit

# Monthly OWASP scan
# Configure with your OWASP ZAP or similar tool
```

### Secret Rotation

```bash
# Update secrets in your deployment system
export PROMPTEASY_AUTH_TOKEN="new-token-value"
export PROMPTEASY_JWT_SECRET="$(openssl rand -base64 32)"

# Restart service to apply new secrets
docker restart prompteasyai
# or
kubectl rollout restart deployment/prompteasyai -n production
```

## Performance Tuning

### Rate Limiting Configuration

```bash
# Adjust based on expected load
export PROMPTEASY_RATE_LIMIT="100"              # per 60 seconds
export PROMPTEASY_REQUESTS_PER_HOUR="5000"      # high volume
export PROMPTEASY_REQUESTS_PER_DAY="50000"      # high volume
```

### Load Testing Results

Expected performance metrics:

```
Concurrent Users: 10
Total Requests: 100
Duration: ~10 seconds
Throughput: 10 req/sec
Average Response Time: 50-100ms
P95 Response Time: 200-300ms
Success Rate: >99%
```

## Incident Response

### Service Down

```bash
# 1. Check service status
curl -v http://localhost:8000/health

# 2. Check logs
docker logs prompteasyai | tail -50

# 3. Verify configuration
python -c "from prompteasy.config import get_settings; s = get_settings(); print(s.get_health_check())"

# 4. If configuration issue, fix and restart
docker restart prompteasyai

# 5. If data corruption suspected, restore backup
python -m prompteasy.cli storage --restore backups/latest.db
docker restart prompteasyai
```

### High Error Rate

```bash
# Check security validation logs
docker logs prompteasyai | grep -i error

# Common issues:
# - Prompt injection detection blocking legitimate requests
# - Quota limits exceeded
# - Database connection issues

# Check quotas configuration
echo $PROMPTEASY_RATE_LIMIT
echo $PROMPTEASY_MAX_PROMPT_LENGTH
```

### Performance Degradation

```bash
# Run load test to measure current performance
python -c "
from prompteasy.performance import LoadTester
result = LoadTester.run_concurrent_test(
    lambda: None, 5, 50
)
print(result.to_dict())
"

# Check system resources
docker stats prompteasyai

# Possible fixes:
# - Scale horizontally (add more replicas in Kubernetes)
# - Increase resource limits
# - Optimize database queries
```

## Upgrade Procedure

```bash
# 1. Backup database
python -m prompteasy.cli storage --backup backups/pre-upgrade.db

# 2. Build new image
docker build -t prompteasyai:0.2.0 .

# 3. Test new image locally
docker run -e PROMPTEASY_ENV=test prompteasyai:0.2.0

# 4. Update deployment
docker pull prompteasyai:0.2.0
docker-compose down
docker-compose up -d

# 5. Verify upgrade
curl http://localhost:8000/health

# 6. If issues, rollback
docker-compose down
python -m prompteasy.cli storage --restore backups/pre-upgrade.db
docker-compose up -d
```

## Summary

Phase 13 provides comprehensive production-ready deployment infrastructure. Follow the deployment checklist and monitoring procedures for safe, reliable production operations.
