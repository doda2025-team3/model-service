FROM python:3.12.9-slim
WORKDIR /app

# Install the dependencies and avoiding to include apt cache in image (F5)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

RUN mkdir -p /models
RUN mkdir -p /app/output

ENV MODEL_DIR=/models
ENV MODEL_PORT="8081"
EXPOSE 8081

ENTRYPOINT ["bash", "run.sh"]
