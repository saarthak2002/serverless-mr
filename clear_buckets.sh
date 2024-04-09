#!/bin/bash

aws s3 rm s3://mr-intermediate --recursive
# aws s3 rm s3://mr-input --recursive
aws s3 rm s3://mr-results-output --recursive