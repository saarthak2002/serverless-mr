import boto3
import json

s3 = boto3.client('s3')
bucket_name = 'mr-output-new'
response = s3.list_objects_v2(Bucket=bucket_name)

wc = dict()

for item in response['Contents']:
    key = item['Key']
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    data = json.loads(obj['Body'].read().decode('utf-8'))
    for k, v in data.items():
        if k not in wc:
            wc[k] = v
        else:
            wc[k] += v
    
wc_sorted = sorted(wc.items(), key=lambda item: item[1], reverse=True)
for word, count in wc_sorted[:20]:
    print(f"{word}, {count}")
