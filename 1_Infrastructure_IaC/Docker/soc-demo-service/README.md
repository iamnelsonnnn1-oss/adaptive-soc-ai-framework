# SOC Demo Service

This is the first Docker workload for the Adaptive SOC AI Framework.

It exposes three demo endpoints:

- `/health`
- `/framework`
- `/telemetry`

## Local Build

```bash
docker build -t soc-demo-service:latest .
```

## Local Run

```bash
docker run --rm -p 8080:8080 soc-demo-service:latest
```

## Example Requests

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/framework
curl http://127.0.0.1:8080/telemetry
```
