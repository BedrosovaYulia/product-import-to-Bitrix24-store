import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    
    #print("I'm being triggered")
    #print(event)
    
    s3=boto3.client("s3")
    if event:
        filename=event['Records'][0]['s3']['object']['key']
        bucketname=event['Records'][0]['s3']['bucket']['name']
        
        print("Filename: ",filename)
        
        fileObj=s3.get_object(Bucket=bucketname, Key=filename)
        
        fileContent=fileObj["Body"].read().decode('utf-8')
        
        print(fileContent)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
