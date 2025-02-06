FROM python:3.11-slim

RUN pip install boto3 requests

WORKDIR /app

COPY github-jenkins-notifier.py .

CMD ["python", "github-jenkins-notifier.py"]