import boto3
import json
import time
from tqdm import tqdm

## Helpful commands
# Clear intermediate results: aws s3 rm s3://mr-intermediate --recursive
# Clear input results: aws s3 rm s3://mr-input --recursive
# Clear output results: aws s3 rm s3://mr-results-output --recursive

## Test inputs
# Small: mr-input-2 (8 files)
# Medium: mr-input (98 files)
# Large: mr-input-3 (932 files)

# mr-input-1
# mr-input-2-new

INPUT_BUCKET = 'mr-input-3-new'
NUM_REDUCERS = 800

start_time = time.time()
end_time = time.time()

total_count = 0
continuation_token = None

s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

def count_files_in_bucket(bucket_name):
    global continuation_token
    global total_count
    while True:
        if continuation_token:
            response = s3_client.list_objects_v2(Bucket=bucket_name, ContinuationToken=continuation_token)
        else:
            total_count = 0
            response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        total_count += len(response['Contents'])

        if 'NextContinuationToken' in response:
            continuation_token = response['NextContinuationToken']
        else:
            break

def main():
    global continuation_token
    global total_count
    all_input = s3_client.list_objects(Bucket=INPUT_BUCKET)['Contents']
    num_mapper = len(all_input)
    
    print("Welcome to Serverless MapReduce")
    print("Number of mappers: {}".format(num_mapper))
    print("Number of reducers: {}".format(NUM_REDUCERS))
    
    # Invoke mapper lambdas for each input file
    print("\n[System] Invoking mappers...")
    with tqdm(total=num_mapper) as pbar:
        for key in all_input:
            resp = lambda_client.invoke( 
                FunctionName = "mapper",
                InvocationType = 'Event',
                Payload =  json.dumps({
                    "mapper_input_file": key["Key"],
                    "number_of_reducers": NUM_REDUCERS,
                    "input_bucket": INPUT_BUCKET,
                })
            )
            pbar.update(1)

    print("\n[System] Waiting for all intermediate files to be ready...")
    while True:
        count_files_in_bucket('mr-intermediate-new')
        print(total_count)
        if total_count == (num_mapper * NUM_REDUCERS):
            print(total_count)
            break
        time.sleep(5)

    print("\n[System] All intermediate files are ready")
    
    total_reducers_ready = 0
    
    print("\n[System] Invoking reducers...")
    with tqdm(total=NUM_REDUCERS) as pbar:
        for reducer_id in range(NUM_REDUCERS):
            # invoke reducer with id reducer_id
            s3_objects_request_response = s3_client.list_objects_v2(Bucket='mr-intermediate-new', Prefix='{}_'.format(reducer_id))
            keys = [item['Key'] for item in s3_objects_request_response['Contents']]
            
            resp = lambda_client.invoke( 
                FunctionName = "reducer",
                InvocationType = 'Event',
                Payload =  json.dumps({
                    "reducer_input_files": keys,
                    "number_of_reducers": NUM_REDUCERS,
                    "reducer_id": reducer_id
                })
            )
            total_reducers_ready += 1
            pbar.update(1)
    
    # check how many outputs are ready
    ready_output = 0
    print("\n[System] Waiting for output...")
    with tqdm(total=NUM_REDUCERS) as pbar:
        while ready_output < NUM_REDUCERS:
            s3_objects_request_response = s3_client.list_objects_v2(Bucket='mr-output-new')
            ready_output = s3_objects_request_response['KeyCount']
            pbar.update(ready_output)
            time.sleep(1)

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print("Execution Time: {}".format(end_time - start_time))