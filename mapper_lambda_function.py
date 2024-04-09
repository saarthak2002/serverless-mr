import json
import boto3

# This is the user map function
# Takes in a K,V pair, returns intermediate K,V pairs as list
def user_map_function(k, v):
    words = []
    filtered_content = ''.join([char if char.isalpha() or char.isspace() or char == "'" else ' ' for char in v])
    words.extend(filtered_content.split())
    kv_list = list()
    for word in words:
        kv_list.append((word.lower(), 1))
    return kv_list
    

def lambda_handler(event, context):
    
    # Get the input file content from the input bucket
    mapper_input_file = event['mapper_input_file']
    s3_client = boto3.client('s3')
    data = s3_client.get_object(Bucket='mr-input', Key=mapper_input_file)
    contents = data['Body'].read().decode('ascii')
    
    # Get the number of reducers
    number_of_reducers = event['number_of_reducers']
    
    # Call the user map function on the input content
    intermediate_kv_pairs = user_map_function(mapper_input_file, contents)

    # Divide the K, V pairs into intermediate buckets
    intermediate_results = [list() for _ in range(number_of_reducers)]
    for kv_pair in intermediate_kv_pairs:
        kv_key = kv_pair[0]
        bucket_id = hash(kv_key) % number_of_reducers
        intermediate_results[bucket_id].append(kv_pair)
    
    s3_resource = boto3.resource('s3')
    bucket_name = 'mr-intermediate'
    
    # Put the content in the intermediate bucket
    for idx, intermediate_result in enumerate(intermediate_results):
        key = '{}_{}_intermediate_output.json'.format(idx, mapper_input_file)
        s3_resource.Object(bucket_name, key).put(Body=json.dumps(intermediate_result))
    
    return True
