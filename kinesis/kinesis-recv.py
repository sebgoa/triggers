#!/usr/bin/env python

import sys#!/usr/bin/env python

import sys
import traceback
import os
import imp
import json
import time

from multiprocessing import Process, Queue
import prometheus_client as prom
import boto3

timeout = float(os.getenv('FUNC_TIMEOUT', 180))

stream_name = 'foobar'
kinesis = boto3.client('kinesis', region_name='us-east-1')
response = kinesis.describe_stream(StreamName=stream_name)

my_shard_id = response['StreamDescription']['Shards'][0]['ShardId']


# loads local foo.py function
mod = imp.load_source('function', 'foo.py')

func = getattr(mod, 'handler')

func_hist = prom.Histogram('function_duration_seconds',
                           'Duration of user function in seconds',
                           ['queue'])
func_calls = prom.Counter('function_calls_total',
                           'Number of calls to user function',
                          ['queue'])
func_errors = prom.Counter('function_failures_total',
                           'Number of exceptions in user function',
                           ['queue'])

def funcWrap(q, payload):
    q.put(func(payload))

def handle(msg):
    func_calls.labels(stream_name).inc()
    with func_errors.labels(stream_name).count_exceptions():
        with func_hist.labels(stream_name).time():
            q = Queue()
            p = Process(target=funcWrap, args=(q,msg,))
            p.start()
            p.join(timeout)
            # If thread is still active
            if p.is_alive():
                p.terminate()
                p.join()
                raise Exception('Timeout while processing the function')
            else:
                return q.get()

if __name__ == '__main__':
    prom.start_http_server(8080)

    shard_iterator = kinesis.get_shard_iterator(StreamName=stream_name,
                                                ShardId=my_shard_id,
                                                ShardIteratorType='LATEST')

    my_shard_iterator = shard_iterator['ShardIterator']

    while True:
        record_response = kinesis.get_records(ShardIterator=my_shard_iterator,
                                              Limit=2)
                                                     
        while 'NextShardIterator' in record_response:
            record_response = kinesis.get_records(ShardIterator=record_response['NextShardIterator'],
                                                  Limit=2)
            try:
                res = handle(record_response)
                sys.stdout.write(str(res) + '\n')
                sys.stdout.flush()

            except Exception:
                traceback.print_exc()
                
            time.sleep(5)

