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

    # Create an SQS client. If region is not provided here, 
    # make sure it's set in your AWS config.
    print(f"Creating boto3 sqs client in region: {aws_region}")

    sqs = boto3.client('sqs', region_name=aws_region)

    # Replace with your actual SQS Queue URL

    print(f"Listening for messages on queue: {sqs_queue_url}")

    while True:
        try:
            # Receive messages from SQS
            response = sqs.receive_message(
                QueueUrl=sqs_queue_url,
                MaxNumberOfMessages=10,       # How many messages to pull at once
                WaitTimeSeconds=10,          # Long-poll for up to 10 seconds
                VisibilityTimeout=30         # How long to keep the message 'invisible' to others
            )

            messages = response.get('Messages', [])
            if not messages:
                # No messages, wait a bit and then poll again
                time.sleep(2)
                continue

            # Process each message
            for message in messages:
                receipt_handle = message['ReceiptHandle']
                body = json.loads(message['Body'])
                body_message = json.loads(body['Message'])
                repository = body_message['repository']

                # Do something with the message
                print(f"Received message: {body}")

                response = requests.get(f"{jenkins_base_url}/git/notifyCommit?url=https://github.com/{github_user}/{repository}.git&branch=master&token={jenkins_token}")
                print("Jenkins notified: " + str(response.status_code))
                print("Body: " + response.text)

                # Once done, delete the message from the queue to prevent reprocessing
                sqs.delete_message(QueueUrl=sqs_queue_url, ReceiptHandle=receipt_handle)
                print("Message deleted from the queue")

        except Exception as e:
            print(f"Encountered an error: {e}")
            # It can be beneficial to add a delay here to avoid tight-looping during errors
            time.sleep(5)

if __name__ == "__main__":
    main()