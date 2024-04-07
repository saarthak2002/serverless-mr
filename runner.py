import boto3
import json

def main():
    s3_client = boto3.client('s3')
    lambda_client = boto3.client('lambda')
    response = s3_client.list_buckets()
    print(response)

    resp = lambda_client.invoke( 
        FunctionName = "mapper",
        InvocationType = 'Event',
        Payload =  json.dumps({
            "payload": "Hello from runner.py"
        })
    )
    print(resp)

if __name__ == '__main__':
    main()