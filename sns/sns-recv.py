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

sns_topic = 'foobar'
sns = boto3.client('sns', region_name='us-east-1')

# Create topic and get Arn, idempotent so will work even if already existing
topic = sns.create_topic(Name=sns_topic)
topic_arn = topic['TopicArn']

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
    func_calls.labels(sns_topic).inc()
    with func_errors.labels(sns_topic).count_exceptions():
        with func_hist.labels(sns_topic).time():
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

