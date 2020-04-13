import os
import json
import boto3
import requests
from urllib.parse import parse_qs
import base64

def http_build_query(params, topkey = ''):
  from urllib.parse import quote
 
  if len(params) == 0:
    return ""
 
  result = ""
 
  # is a dictionary?
  if type (params) is dict:
    for key in params.keys():
      newkey = quote (key)
      if topkey != '':
        newkey = topkey + quote('[' + key + ']')
 
      if type(params[key]) is dict:
        result += http_build_query (params[key], newkey)
 
      elif type(params[key]) is list:
        i = 0
        for val in params[key]:
          result += newkey + quote('[' + str(i) + ']') + "=" + quote(str(val)) + "&"
          i = i + 1
 
      # boolean should have special treatment as well
      elif type(params[key]) is bool:
        result += newkey + "=" + quote (str(int(params[key]))) + "&"
 
      # assume string (integers and floats work well)
      else:
        result += newkey + "=" + quote (str(params[key])) + "&"
 
  # remove the last '&'
  if (result) and (topkey == '') and (result[-1] == '&'):
    result = result[:-1]
 
  return result

def add_b24_product(key, name, price, file_url, xml_id):
  
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

  response = requests.post(key+"crm.product.add",http_build_query(product_data))
  result=response.json()
  
  return result["result"]
  
  
def update_b24_product(bitrix_id, key, name, price, file_url, xml_id):
  
  import requests
  import base64
  
  print("Апдейт товара с ИД ",bitrix_id)
  
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

  response = requests.post(key+"crm.product.update",http_build_query(product_data))
  result=response.json()
  
  return result["result"]
  

DYNAMODB = boto3.resource('dynamodb','us-east-1')
TABLE = DYNAMODB.Table('B24_products')

def lambda_handler(event, context):
    # TODO implement
    
    print(event)
    
    for Record in event["Records"]:
        if Record["eventName"]=="INSERT" and Record["dynamodb"]["NewImage"]["bitrix_id"]["S"]=='0':
            
            offer=Record["dynamodb"]["NewImage"]
            
            #отпроцессить картинку, положить результат во 2ю таблицу, где будут накапливаться запросы к Б24
            #пока для теста сразу бахнем запрос к Битрикс24
            key=os.environ['B24key']
            bitrix_id=add_b24_product(key, offer["product_name"]["S"], offer["product_price"]["S"], offer["product_picture"]["S"], offer["id"]["N"])
            print("В Битрикс24 добавлен товар с ИД: ",bitrix_id)
            
            #Дописываем ид товара Битрикс24 в таблицу товаров
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
            
            #отпроцессить картинку, положить результат во 2ю таблицу, где будут накапливаться запросы к Б24
            #пока для теста сразу бахнем запрос к Битрикс24
            
            #Обновляем цену только если она изменилась
            if offer["product_price"]["S"]!=offer_old["product_price"]["S"]:
              key=os.environ['B24key']
              result=update_b24_product(offer_old["bitrix_id"]["N"], key, offer["product_name"]["S"], offer["product_price"]["S"], offer["product_picture"]["S"], offer["id"]["N"])
              print(result)
            
            #возвращаем на место битрикс_ид
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
