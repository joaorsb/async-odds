import requests
import json


def get_events(url, header, start_date, end_date):
    jsonrpc_req='{\
            "jsonrpc": "2.0",\
            "method": "SportsAPING/v1.0/listEvents",\
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

    try:
        events_full = json.loads(response.text)['result']
        for ev in events_full:
            events.append(ev['event']['id'])
    except KeyError:
        error = json.loads(response.text)['error']['data']['APINGException']['errorCode']
        events.append(error)

    return json.dumps(events)
