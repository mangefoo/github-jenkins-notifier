import os
import boto3
import time
import requests
import json

def main():
    aws_region = os.environ['AWS_REGION']
    jenkins_base_url = os.environ['JENKINS_BASE_URL']
    jenkins_token = os.environ['JENKINS_TOKEN']
    github_user = os.environ['GITHUB_USER']
    sqs_queue_url = os.environ['SQS_QUEUE_URL']

    print(f"Creating boto3 sqs client in region: {aws_region}")

    sqs = boto3.client('sqs', region_name=aws_region)

    print(f"Listening for messages on queue: {sqs_queue_url}")

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=sqs_queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10,
                VisibilityTimeout=30
            )

            messages = response.get('Messages', [])
            if not messages:
                time.sleep(2)
                continue

            for message in messages:
                receipt_handle = message['ReceiptHandle']
                body = json.loads(message['Body'])
                body_message = json.loads(body['Message'])
                repository = body_message['repository']

                print(f"Received message: {body}")

                response = requests.get(f"{jenkins_base_url}/git/notifyCommit?url=https://github.com/{github_user}/{repository}.git&branch=master&token={jenkins_token}")
                print("Jenkins notified: " + str(response.status_code))
                print("Body: " + response.text)

                sqs.delete_message(QueueUrl=sqs_queue_url, ReceiptHandle=receipt_handle)
                print("Message deleted from the queue")

        except Exception as e:
            print(f"Encountered an error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()