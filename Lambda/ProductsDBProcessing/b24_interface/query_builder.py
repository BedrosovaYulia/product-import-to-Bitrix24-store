class B24QueryBuilder:
  
    @staticmethod
    def add_b24_product(name, price, file_url, xml_id):
      """(str, str, str, str) -> str
      The function prepares a urlencoded string of request parameters 
      for the subsequent call of the Bitrix24 rest-api.
      """
      
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
    
      return product_data
    
    @staticmethod
    def update_b24_product(bitrix_id, name, price, file_url, xml_id):
      """(str, str, str, str, str) -> str
      The function prepares a urlencoded string of request parameters 
      for the subsequent call of the Bitrix24 rest-api.
      """
      
      import requests
      import base64
      import boto3
      
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
      
      return product_data
