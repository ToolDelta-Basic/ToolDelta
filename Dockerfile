
FROM python:3.12-slim
ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app

WORKDIR /app

COPY . /app/

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN apt-get update && \
    apt-get install -y --no-install-recommends g++ zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir . && \
    rm -rf /app/*

CMD ["python", "-c", "from tooldelta.launch_options import client_title; import os; client_title(); os._exit(0)"]
