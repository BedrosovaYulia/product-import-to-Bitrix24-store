import json
import os
from bitrix24 import Bitrix24

  
def lambda_handler(event, context):
    

        domain=os.environ['domain']
        key=os.environ['key']
        
        bx24 = Bitrix24(domain, user_id=1)
        
        params = {'id': 310}
        result = bx24.call_webhook('crm.product.get', key, params=params)
        print(result)
        
        
        calls = {
            'get_user': ('user.current', {}),
            'get_product_310': {
                'method': 'crm.product.get',
                'params': {'ID': 310}
            },
            'get_product_328': {
                'method': 'crm.product.get',
                'params': {'ID': 328}
            }
        }
        result = bx24.call_batch_webhook(calls, key, True)
        print(result)

        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }


