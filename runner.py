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

INPUT_BUCKET = 'mr-input-3'
NUM_REDUCERS = 800

start_time = time.time()
end_time = time.time()

def main():
    s3_client = boto3.client('s3')
    lambda_client = boto3.client('lambda')
    all_input = s3_client.list_objects(Bucket=INPUT_BUCKET)['Contents']
    num_mapper = len(all_input)
    
    print("Welcome to Serverless MapReduce")
    print("Number of mappers: {}".format(num_mapper))
    print("Number of reducers: {}".format(NUM_REDUCERS))
    # Invoke mapper lambdas for each input file
    print("\n[System] Invoking mappers...")
    with tqdm(total=num_mapper) as pbar:
        for key in all_input:
            # print("call mapper on {}".format(key))
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
        # print(resp)

    total_reducers_ready = 0
    reducer_ready = [False] * NUM_REDUCERS
    # print(reducer_ready)
    
    print("\n[System] Invoking reducers...")
    with tqdm(total=NUM_REDUCERS) as pbar:
        while total_reducers_ready < NUM_REDUCERS:
            for reducer_id in range(NUM_REDUCERS):
                s3_objects_request_response = s3_client.list_objects_v2(Bucket='mr-intermediate', Prefix='{}_'.format(reducer_id))
                key_count = s3_objects_request_response['KeyCount']
                
                num_inter_files = 0
                if key_count > 0:
                    num_inter_files = len(s3_objects_request_response['Contents'])
                
                if num_inter_files == num_mapper:
                    reducer_ready[reducer_id] = True
                    total_reducers_ready += 1
                    # invoke reducer with id reducer_id
                    
                    keys = [item['Key'] for item in s3_objects_request_response['Contents']]
                    # print("call reducer {}".format(reducer_id))
                    # print("with files: {}".format(keys))
                    resp = lambda_client.invoke( 
                        FunctionName = "reducer",
                        InvocationType = 'Event',
                        Payload =  json.dumps({
                            "reducer_input_files": keys,
                            "number_of_reducers": NUM_REDUCERS,
                            "reducer_id": reducer_id
                        })
                    )
                    pbar.update(1)
                    
                    # print(resp)
                    
            # print(reducer_ready)
            time.sleep(1)
    
    # check how many outputs are ready
    ready_output = 0
    print("\n[System] Waiting for output...")
    with tqdm(total=NUM_REDUCERS) as pbar:
        while ready_output < NUM_REDUCERS:
            s3_objects_request_response = s3_client.list_objects_v2(Bucket='mr-results-output')
            ready_output = s3_objects_request_response['KeyCount']
            pbar.update(ready_output)
            time.sleep(1)

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print("Execution Time: {}".format(end_time - start_time))