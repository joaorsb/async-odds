import requests
import json


def get_odds(url, header, market_id):
    jsonrpc_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook",  "params": {\
            "marketIds": ["' + market_id + '"], \
            "priceProjection": {\
                "priceData": ["EX_BEST_OFFERS", "EX_TRADED"],\
                "virtualise": "true"\
            }\
        }, "id": 1}'

    response = requests.post(url, data=jsonrpc_req, headers=header)
    odds_response = json.loads(response.text)['result'][0]

    # print(odds_response)
    return odds_response['runners']


async def get_odds_async(session, url, header, market_id):
    jsonrpc_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook",  "params": {\
                    "marketIds": ["' + market_id + '"], \
                    "priceProjection": {\
                        "priceData": ["EX_BEST_OFFERS", "EX_TRADED"],\
                        "virtualise": "true"\
                    }\
                }, "id": 1}'
    async with session.post(url, data=jsonrpc_req, headers=header) as response:
        data = await response.text()
        odds_response = json.loads(data)['result'][0]

    return odds_response['runners']
