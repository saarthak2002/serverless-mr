import boto3
import json

## Helpful commands
# Clear intermediate results: aws s3 rm s3://mr-intermediate --recursive

NUM_REDUCERS = 7

def main():
    s3_client = boto3.client('s3')
    lambda_client = boto3.client('lambda')
    all_input = s3_client.list_objects(Bucket='mr-input')['Contents']
    num_mapper = len(all_input)
    print(num_mapper)
    for key in all_input:
        resp = lambda_client.invoke( 
            FunctionName = "mapper",
            InvocationType = 'Event',
            Payload =  json.dumps({
                "mapper_input_file": key["Key"],
                "number_of_reducers": NUM_REDUCERS
            })
        )
        print(resp)


    ## IGNORE:
    # words = []
    # data = s3_client.get_object(Bucket='mr-input', Key='pg-dorian_gray.txt')
    # contents = data['Body'].read().decode('ascii')
    # filtered_content = ''.join([char if char.isalpha() or char.isspace() or char == "'" else ' ' for char in contents])
    # words.extend(filtered_content.split())
    # kv_list = list()
    # for word in words:
    #     kv_list.append((word.lower(), 1))
    # print(json.dumps(kv_list))
    # # mr-intermediate
    # intermediate_results = [list() for _ in range(5)]
    # for kv_pair in kv_list:
    #     kv_key = kv_pair[0]
    #     bucket_id = hash(kv_key) % 5
    #     intermediate_results[bucket_id].append(kv_pair)
    # print(intermediate_results)

    # print(contents)
    # filtered_content = ''.join([char if char.isalpha() or char.isspace() or char == "'" else ' ' for char in contents])
    # print(filtered_content)
    # corpus.extend(filtered_content.split())

    # for key in s3_client.list_objects(Bucket='mr-input')['Contents']:
    #     data = s3_client.get_object(Bucket='mr-input', Key=key["Key"])
    #     contents = data['Body'].read()
    #     print(contents)

    
    # response = s3_client.list_buckets()
    # print(response)

    # resp = lambda_client.invoke( 
    #     FunctionName = "mapper",
    #     InvocationType = 'Event',
    #     Payload =  json.dumps({
    #         "payload": "Hello from runner.py"
    #     })
    # )
    # print(resp)

if __name__ == '__main__':
    main()