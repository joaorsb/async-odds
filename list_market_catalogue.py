import requests
import json
from itertools import groupby


def get_markets(url, header, event_ids=None, match_qty=None):
    if not match_qty:
        match_qty = 999

    jsonrpc_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", \
                    "params": {"filter": {"eventIds": ' + event_ids + ', \
                    "marketTypeCodes": []},\
                    "maxResults": ' + str(match_qty) + ',"marketProjection": \
                    ["COMPETITION","EVENT","EVENT_TYPE", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]},\
                    "id": 1}'

    response = requests.post(url, data=jsonrpc_req, headers=header)
    try:
        results = json.loads(response.text)['result']
        grouped_results = [list(g) for k, g in
                           groupby(sorted(results, key=lambda x: x['event']['id']), lambda x: x['event']['id'])]

        matches = []
        for markets in grouped_results:
            match = {}
            match['other_markets'] = []
            for result in markets:
                if result['eventType']['id'] == '1':
                    try:
                        if result['marketName'] == 'Match Odds':
                            match['marketId'] = result['marketId']
                            match['marketStartTime'] = result['marketStartTime']
                            match['homeTeam'] = {}
                            match['awayTeam'] = {}
                            match['draw'] = {}
                            match['homeTeam']['selectionId'] = result['runners'][0]['selectionId']
                            match['homeTeam']['runnerName'] = result['runners'][0]['runnerName']
                            match['awayTeam']['selectionId'] = result['runners'][1]['selectionId']
                            match['awayTeam']['runnerName'] = result['runners'][1]['runnerName']
                            match['draw']['selectionId'] = result['runners'][2]['selectionId']
                            match['draw']['runnerName'] = result['runners'][2]['runnerName']
                            match['competition'] = result['competition']['name'] if 'competition' in result else ""
                            match['eventId'] = result['event']['id']
                            match['eventName'] = result['event']['name']
                        elif result['marketName'] == "Over/Under 2.5 Goals":
                            match['over_25'] = {}
                            match['over_25']['marketId'] = result['marketId']
                            match['over_25']['over'] = {}
                            match['over_25']['over']['selectionId'] = result['runners'][1]['selectionId']
                            match['over_25']['over']['runnerName'] = result['runners'][1]['runnerName']
                            match['over_25']['under'] = {}
                            match['over_25']['under']['selectionId'] = result['runners'][0]['selectionId']
                            match['over_25']['under']['runnerName'] = result['runners'][0]['runnerName']
                        else:
                            market = {}
                            market[result['marketName']] = result
                            match['other_markets'].append(market)

                    except IndexError:
                        print(match)
                        pass

            if 'marketId' in match and ' Unmanaged' not in result['marketName']:
                matches.append(match)
                # else:
                # print(result)
        return matches
    except KeyError:
        results = json.loads(response.text)['error']
        print(json.loads(response.text))
        return results
