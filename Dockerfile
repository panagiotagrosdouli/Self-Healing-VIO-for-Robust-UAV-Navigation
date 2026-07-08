FROM python:3.11-slim

WORKDIR /workspace/SHIELD-VIO
COPY . .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy pytest pyyaml
ENV PYTHONPATH=/workspace/SHIELD-VIO/src
CMD ["bash", "-lc", "python scripts/demo_health_monitor.py && pytest -q"]
