FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY zhol ./zhol
COPY web ./web
ENV ZHOL_DB=/data/zhol.db
VOLUME ["/data"]
EXPOSE 8000
CMD ["uvicorn", "zhol.api:app", "--host", "0.0.0.0", "--port", "8000"]
