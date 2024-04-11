# Serverless MapReduce

![Serverless MapReduce Architecture Diagram](https://i.imgur.com/SQjgR7Q.png)

MapReduce is a scalable computation model that allows batch processing of enormous datasets. Serverless computing is a cloud programming paradigm in which software can be deployed with resources allocated on-demand without the need to manage server infrastructure. We wanted to bring these two models together and create a Serverless MapReduce implementation that provides the advantages of both worlds, like cost-effectiveness and parallelism. We used AWS Lambda to invoke cloud functions that perform map or reduce tasks and AWS S3 as a distributed object store for inputs, outputs, and intermediate data.

## Code files

The files in this repository are described below:

_runner.py_: Client side code used by the user to schedule map and reduce workers.

_mapper\_lambda\_function.py_: Code running on the Mapper AWS Lambda instances. The user defines a _Map(K, V) → [(K, V)]_ function here.

_reducer\_lambda\_handler.py_: Code running on the Reducer AWS Lambda instances. The user defines a _Reduce(K, Val-list) → Output_ function here.

_process\_output.py_: Tester file to combine the output of the word count example job.