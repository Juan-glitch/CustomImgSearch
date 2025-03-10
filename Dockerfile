FROM python:3.12-slim
WORKDIR /src
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["sleep", "infinity"]
