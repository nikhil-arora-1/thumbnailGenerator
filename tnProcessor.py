import boto3
from PIL import Image
import json
import os
import logging

sqsQueueName = 'tn-gen-queue' #os.environ.get('QNAME') 
destinationFolderName = 'Processed' #os.environ.get('DESTDIR')
MAX_SIZE = (100, 100)
TB_PREFIX = "tb-"

logging.basicConfig(filename='tnGen.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def getUrl(jsonString):
    s3 = json.loads(jsonString)
    s3 = s3['Records'][0]['s3']
    global bucketName
    bucketName = s3['bucket']['name']
    global objectName
    objectName = s3['object']['key']


def getImage():
    s3 = boto3.client('s3')
    global fileName
    fileName = objectName.split('/')[-1]
    basePath = os.path.dirname(__file__)
    imageFilePath = os.path.join(basePath, fileName)
    s3.download_file(bucketName, objectName, imageFilePath)
    image = Image.open(f"{imageFilePath}")
    return image


def createThumbnail(image):
    image.thumbnail(MAX_SIZE)
    image.save(TB_PREFIX + f'{fileName}')
    return TB_PREFIX + f'{fileName}'


def uploadThumbnail(thumbnailFilePath):
    s3 = boto3.client('s3')
    response = ''
    targetObj = destinationFolderName + "/" + TB_PREFIX + fileName
    with open(thumbnailFilePath, "rb") as f:
        response = s3.upload_fileobj(f, bucketName, targetObj)
    return response


# Choosing the resource from boto3 module
sqs = boto3.resource('sqs')

# Get the queue named test
queue = sqs.get_queue_by_name(QueueName = sqsQueueName)

# Process messages
while True:
    try:
        for message in queue.receive_messages():
            # get S3 object URL from message body
            logging.error("Message: " + message.body)
            getUrl(message.body)
            # download the S3 object to a temp folder
            image = getImage()
            # generate thumbnail for the temp object
            thumbnail = createThumbnail(image)
            # upload generated thumbnail to a new S3 bucket
            targetUrl = uploadThumbnail(thumbnail)
            # delete message from queue once processed
            message.delete()
    except KeyError:
        logging.error("An error occurred: KeyError")
    except Exception as e:
        logging.error("some error occurred: " + e)
        pass