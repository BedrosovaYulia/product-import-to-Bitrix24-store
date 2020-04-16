import os
import json
import boto3
from xml.dom import minidom

DYNAMODB = boto3.resource('dynamodb','us-east-1')
TABLE = DYNAMODB.Table('B24_products')
        

def lambda_handler(event, context):
    # TODO implement
    
    #print("I'm being triggered")
    print(event)
    
    s3=boto3.client("s3")
    if event:
        filename=event['Records'][0]['s3']['object']['key']
        bucketname=event['Records'][0]['s3']['bucket']['name']
        
        print("Filename: ",filename)
        
        fileObj=s3.get_object(Bucket=bucketname, Key=filename)
        
        fileContent=fileObj["Body"].read().decode('utf-8')
        
        #parse xml
        xmldoc = minidom.parseString(fileContent)
        offers = xmldoc.getElementsByTagName('offer')
        
        k=0
        for offer in offers:
            if k<15 or os.environ['test_mode']=='off':
                k+=1
        
                product_name = offer.getElementsByTagName("name")[0].firstChild.data
                product_price = offer.getElementsByTagName("price")[0].firstChild.data
                product_picture = offer.getElementsByTagName("picture")[0].firstChild.data
        
                attrs = dict(offer.attributes.items())
        
                product_id=attrs["id"]
                product_available=attrs["available"]
        
                #save data in database
    
                item = {'id':int(product_id)}
        
                item['product_available']=product_available
                item['product_name']=product_name
                item['product_price']=product_price
                item['product_picture']=product_picture
                item['bitrix_id']=0
                print(product_id)
                TABLE.put_item(Item=item)
                
            else:
                break
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
