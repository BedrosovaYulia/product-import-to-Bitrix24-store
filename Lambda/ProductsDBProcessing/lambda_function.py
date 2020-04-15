import os
import json
import boto3
#Bitrix24 lib - in Layers
from bitrix24 import Bitrix24

domain=os.environ['domain']
key=os.environ['key']
        
bx24 = Bitrix24(domain, user_id=1)

def add_b24_product(name, price, file_url, xml_id):
  
  import requests
  import base64
  
  content1=requests.get(file_url).content
  image_64_encode = str(base64.b64encode(content1))[2:-1]
  
  product_data = {
    "fields" : {
      "iblockId": 1,
      "NAME" : name,
      "CURRENCY_ID": "RUB",
      "PRICE" : price,
      "XML_ID":xml_id,
      "PREVIEW_PICTURE": {
        "fileData":dict()
        }
      }
    }
        
  product_data["fields"]["PREVIEW_PICTURE"]["fileData"]['0']="1.png"
  product_data["fields"]["PREVIEW_PICTURE"]["fileData"]['1']=image_64_encode

  result = bx24.call_webhook('crm.product.add', key, params=product_data)
  
  return result["result"]
  
  
def update_b24_product(bitrix_id, name, price, file_url, xml_id):
  
  import requests
  import base64
  import boto3
  
  print("Product update with id ",bitrix_id)
  
  content1=requests.get(file_url).content
  image_64_encode = str(base64.b64encode(content1))[2:-1]
  
  product_data = {
    "id":bitrix_id,
    "fields" : {
      "iblockId": 1,
      "NAME" : name,
      "CURRENCY_ID": "RUB",
      "PRICE" : price,
      "XML_ID":xml_id,
      "PREVIEW_PICTURE": {
        "fileData":dict()
        }
      }
    }
        
  product_data["fields"]["PREVIEW_PICTURE"]["fileData"]['0']="1.png"
  product_data["fields"]["PREVIEW_PICTURE"]["fileData"]['1']=image_64_encode
  
  #response = requests.post(key+"crm.product.update",http_build_query(product_data))
  #result=response.json()
  
  result = bx24.call_webhook('crm.product.update', key, params=product_data)
  
  return result
    
DYNAMODB = boto3.resource('dynamodb','us-east-1')
TABLE = DYNAMODB.Table('B24_products')

def lambda_handler(event, context):
    # TODO implement
    
    print(event)
    
    for Record in event["Records"]:
        if Record["eventName"]=="INSERT" and Record["dynamodb"]["NewImage"]["bitrix_id"]["S"]=='0':
            
            offer=Record["dynamodb"]["NewImage"]
            
            #process the picture, put the result in the queue, where requests to B24 will accumulate
            #while for the test we’ll immediately make a request to Bitrix24
            
            bitrix_id=add_b24_product(offer["product_name"]["S"], offer["product_price"]["S"], offer["product_picture"]["S"], offer["id"]["N"])
            print("in Bitrix24 added product with ID: ",bitrix_id)
            
            #add Bitrix24 product id to the product table
            response = TABLE.update_item(
              Key={
                  'id': int(offer["id"]["N"]),
                },
              UpdateExpression="set bitrix_id = :r",
              ExpressionAttributeValues={
                  ':r': bitrix_id,
              },
              ReturnValues="UPDATED_NEW"
            )
            
        
        if Record["eventName"]=="MODIFY":
          
            offer=Record["dynamodb"]["NewImage"]
            offer_old=Record["dynamodb"]["OldImage"]
            
            #process the picture, put the result in the queue, where requests to B24 will accumulate
            #while for the test we’ll immediately make a request to Bitrix24
            
            #We update the price only if it has changed
            if offer["product_price"]["S"]!=offer_old["product_price"]["S"]:
              
              result=update_b24_product(offer_old["bitrix_id"]["N"], offer["product_name"]["S"], offer["product_price"]["S"], offer["product_picture"]["S"], offer["id"]["N"])
              print(result)
            
            #return bitrix_id to the place
            response = TABLE.update_item(
              Key={
                  'id': int(offer["id"]["N"]),
                },
              UpdateExpression="set bitrix_id = :r",
              ExpressionAttributeValues={
                  ':r': offer_old["bitrix_id"]["N"],
              },
              ReturnValues="UPDATED_NEW"
            )
        
            
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
