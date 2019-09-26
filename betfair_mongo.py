import datetime
import os
import time

from pymongo import MongoClient
import urllib.parse
from aiohttp import ClientSession
from unsync import unsync

from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin.exceptions
from google.api_core import exceptions

from list_events import get_events
from list_market_catalogue import get_markets
from list_market_book import get_odds, get_odds_async
from login import create_token_betfair, delete_token, get_or_create_token


cred = credentials.Certificate('')
firebase_admin.initialize_app(cred)

db = firestore.client()
token = ''


def main():
    global token, db

    try:
        if token == "":
            token = get_or_create_token(db)

        main_tasks = []
        for i in range(8):
            main_tasks.append(get_odds(db, i))

        [task.result() for task in main_tasks]

    except exceptions.ResourceExhausted:
        token = create_token_betfair()

    print("termino da consulta, sleep")
    time.sleep(300)


@unsync
def get_odds(db, day_to_sum):
    global token
    password = urllib.parse.quote_plus(os.environ.get('MONGO_PASSWORD'))
    mongo_client = MongoClient(
        "mongodb+srv://joao:%s@maincluster-he8du.gcp.mongodb.net/test?retryWrites=true&w=majority" %  password
    )

    mongo_db = mongo_client.betfair_odds
    collection = mongo_db.bf_events

    # Betfair api url and keys
    url = "https://api.betfair.com/betting/json-rpc"
    header = {'X-Application': os.environ.get("BF_APP_ID"),
              'X-Authentication': str(token),
              'content-type': 'application/json'}

    first_date = (datetime.datetime.utcnow() + datetime.timedelta(days=day_to_sum)).strftime("%Y-%m-%dT%TZ")
    last_date = (datetime.datetime.utcnow() + datetime.timedelta(days=day_to_sum + 1)).strftime("%Y-%m-%dT%TZ")
    events_ids = get_events(url, header, start_date=first_date, end_date=last_date)
    if day_to_sum > 8:
        print(events_ids)
    if "INVALID_SESSION_INFORMATION" in events_ids:
        delete_token(db)
        token = get_or_create_token(db)

    if len(events_ids) > 0:
        matches = get_markets(url, header, events_ids)
        if 'code' not in matches:
            odds_tasks = []
            for match in matches:
                odds_tasks.append(retrieve_matches_and_save(collection, match, url, header))

            [odd_task.result() for odd_task in odds_tasks]
    else:
        print(events_ids)
        token = get_or_create_token(db)

    print("Terminada iteração {}".format(day_to_sum))


@unsync
async def retrieve_matches_and_save(collection, match, url, header):
    async with ClientSession() as session:
        if 'over_25' in match:
            over_25 = await get_odds_async(session, url, header, match['over_25']['marketId'])

            for price in over_25:
                if price['selectionId'] == match['over_25']['under']['selectionId']:
                    match['over_25']['under']['odds'] = price['ex']
                else:
                    match['over_25']['over']['odds'] = price['ex']

        match_odds = await get_odds_async(session, url, header, match['marketId'])
        for price in match_odds:
            if price['selectionId'] == match['homeTeam']['selectionId']:
                match['homeTeam']['odds'] = price['ex']
            elif price['selectionId'] == match['awayTeam']['selectionId']:
                match['awayTeam']['odds'] = price['ex']
            else:
                match['draw']['odds'] = price['ex']

        if len(match['homeTeam']['odds']['availableToLay']) > 0 \
                or len(match['awayTeam']['odds']['availableToLay']) > 0 or \
                len(match['draw']['odds']['availableToLay']) > 0:
            event = {'event_id': match['eventId'], 'markets': match}
            match['lastSaved'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%TZ")
            collection.update_one({'event_id': event['event_id']}, {'$set': event}, upsert=True)
        else:
            print("Sem odd para registrar em: {}".format(match['eventName']))


if __name__ == "__main__":
    main()

