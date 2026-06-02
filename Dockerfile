FROM python:3.12-slim

WORKDIR /app

COPY starter_v0/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY starter_v0 .

EXPOSE 8501

CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.headless=true"]
