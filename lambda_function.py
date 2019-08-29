import json
import boto3
import datetime
import math
import time
import sys
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

s3_client = boto3.client('s3')
logs_client = boto3.client('logs')

bucket_name = os.environ['bucket_name']
nDays = int(os.environ['days'])
deletionDate = datetime.datetime.now() - datetime.timedelta(days=nDays)
startOfDay = deletionDate - datetime.timedelta(days=1000)
startOfDay = startOfDay.replace(hour=0, minute=0, second=0, microsecond=0)
endOfDay = deletionDate.replace(hour=23, minute=59, second=59, microsecond=999999)

def lambda_handler(event, context):
    try:
        for logGroupName in getCloudWatchLogGroups():  
            try:
                logging.info("logGroupName = %s" % logGroupName)
                response = createExportTask(logGroupName)

                waitForExportTaskToComplete(response['taskId'])
                streams = getLogsStreamByLogGroupName(logGroupName, endOfDay)
                
                for stream in streams:    
                    logging.info("# Deleting %s " % stream['logStreamName'])
                    deleteStreams(logGroupName, stream['logStreamName'])        
                    
            except Exception as e:
                logging.error("No valid JSON message: %s", parsed_message)

    except Exception as e:
        logging.error("Error: %s", str(e))

def deleteStreams(logGroupName, logStreamName):
    response = logs_client.delete_log_stream(
        logGroupName=logGroupName,
        logStreamName=logStreamName)

def waitForExportTaskToComplete(taskId):
    
    taskDetails = logs_client.describe_export_tasks(taskId=taskId)
    task = taskDetails['exportTasks'][0]
    taskStatus = task['status']['code'];
    
    if (taskStatus == 'RUNNING' or taskStatus == 'PENDING') :    
        logging.info('Task is running for %s with stats %s ' % ( task['logGroupName']  , task['status']));
        time.sleep( 1 )
        return waitForExportTaskToComplete(taskId)
    
    logging.info('Task is fineshed for %s with stats %s ' % ( task['logGroupName']  , task['status']));
    return True

def getCloudWatchLogGroups():
    groupnames = []
    paginator = logs_client.get_paginator('describe_log_groups')
    response_iterator = paginator.paginate()
    
    for response in response_iterator:
        listOfResponse = response["logGroups"]
        for result in listOfResponse:
            try:
                if not result['retentionInDays']:
                    logging.debug('retentionInDays = %s' % result['retentionInDays'])
            except:
                groupnames.append(result["logGroupName"])
                pass
    return groupnames

def createExportTask(logGroupName):
    log_path_for_s3 = getLogPathForS3(logGroupName)
    
    export_task = logs_client.create_export_task(
        taskName='export_task',
        logGroupName=logGroupName,
        fromTime=math.floor(startOfDay.timestamp() * 1000), 
        to=math.floor(endOfDay.timestamp() * 1000), 
        destination= bucket_name, 
        destinationPrefix=log_path_for_s3)
    
    return export_task

def getLogPathForS3(logGroupName):
    try:
        path = logGroupName
        if logGroupName.startswith('/'):
            path = logGroupName[1:]
        
        logging.info( getDatePath() + "/" + path)
        return  path + "/" + getDatePath()
    except Exception as e:
        logging.error("Error: %s", str(e))

def getDatePath():
    return datetime.datetime.now().strftime('%Y%m%d')

def getLogsStreamByLogGroupName(logGroupName, endOfDay):
    try: 
        deleteLogsStream = []
        log_streams = None
        next_token = None

        while True:
            if next_token:
                log_streams = logs_client.describe_log_streams(
                    logGroupName=logGroupName,
                    orderBy='LastEventTime',
                    descending=True,
                    nextToken=next_token)
            else:
                log_streams = logs_client.describe_log_streams(
                    logGroupName=logGroupName, 
                    descending=True,
                    orderBy='LastEventTime')

            next_token = log_streams.get('nextToken', None)
            
            for stream in log_streams['logStreams']:
                log_stream_name = stream['logStreamName']

                readable =  datetime.datetime.fromtimestamp(float(stream['creationTime'])/1000)
                if stream['storedBytes'] > 0:
                    readable =  datetime.datetime.fromtimestamp(float(stream['lastEventTimestamp'])/1000)
                
                if readable  < endOfDay: 
                    deleteLogsStream.append(stream)

            if not next_token or len(log_streams['logStreams']) == 0:            
                break

        return deleteLogsStream
    except Exception as e:
        logging.error("Error: %s", str(e))
