FROM python:3.12.9-slim
WORKDIR /app

# Install the dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

ENV MODEL_PORT="8081"
EXPOSE 8081

ENTRYPOINT ["bash", "run.sh"]
