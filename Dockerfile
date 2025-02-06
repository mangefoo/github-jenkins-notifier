FROM python:3.11-slim

WORKDIR /app

COPY github-jenkins-notifier.py .

CMD ["python", "github-jenkins-notifier.py"]