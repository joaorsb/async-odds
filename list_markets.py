import requests
import json


def get_markets_types(url, header, start_date, end_date):
    jsonrpc_req='{\
            "jsonrpc": "2.0",\
            "method": "SportsAPING/v1.0/listMarketTypes",\
            "params": {\
                "filter": {\
                    "eventTypeIds": [\
                        "1"\
                    ],\
                    "marketStartTime": {\
                        "from": "' + start_date + '",\
                        "to": "' + end_date + '"\
                    }\
                }\
            },\
            "id": 1\
        }'
    response = requests.post(url, data=jsonrpc_req, headers=header)
    events = []
    print(json.dumps(json.loads(response.text)['result'], indent=2))

    # try:
    #     events_full = json.loads(response.text)['result']
    #     for ev in events_full:
    #         # print(ev)
    #         events.append(ev['event']['id'])
    # except KeyError:
    #     error = json.loads(response.text)['error']['data']['APINGException']['errorCode']
    #     events.append(error)
    #
    # return json.dumps(events)
