
FROM python:3.12-slim
ENV TZ Asia/Shanghai
ENV PYTHONPATH=/app

WORKDIR /app

COPY . /app/

RUN pip3 install . && \
    rm -rf /app/*

CMD ["python", "-c", "import tooldelta; tooldelta.start_tool_delta()"]
