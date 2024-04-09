import json
import boto3

s3_client = boto3.client('s3')

def user_reduce_function(k, val_list):
    return len(val_list)

def read_json_from_s3(bucket_name, file_key):
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    json_data = json.loads(obj['Body'].read().decode('utf-8'))
    return json_data

def lambda_handler(event, context):
    reducer_input_files = event['reducer_input_files']
    reducer_id = event['reducer_id']
    
    bucket_name = 'mr-intermediate'
    all_json_data = []
    
    for file_key in reducer_input_files:
        # Read JSON data from S3
        json_data = read_json_from_s3(bucket_name, file_key)
        # Append JSON data to array
        all_json_data.extend(json_data)

    intermediate_dict = dict()
    output = dict()

    # Convert the intermediate K,V pairs into K, val-list format
    for kv_pair in all_json_data:
        kv_pair_key = kv_pair[0]
        kv_pair_val = kv_pair[1]
        
        if kv_pair_key in intermediate_dict:
            intermediate_dict[kv_pair_key].append(kv_pair_val)
        else:
            intermediate_dict[kv_pair_key] = list()
            intermediate_dict[kv_pair_key].append(kv_pair_val)
    
    for k, v in intermediate_dict.items():
        output[k] = user_reduce_function(k, v)
    
    output_key = "{}_output.json".format(reducer_id)
    s3_client.put_object(Bucket="mr-results-output", Key=output_key, Body=json.dumps(output))
    
    return True
