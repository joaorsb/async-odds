import urllib.parse
import arrow
import motor.motor_asyncio
import asyncio
import os


def main():
    print("Começo do trabalho")
    main_db_collection = create_main_connection()
    bkp_db_collection = create_bkp_connection()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_all_items(main_db_collection, bkp_db_collection))


def create_main_connection():
    password = urllib.parse.quote_plus(os.environ.get('MONGO_PASSWORD'))
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb+srv://joao:%s@maincluster-he8du.gcp.mongodb.net/test?retryWrites=true&w=majority" % password
    )
    mongo_db = mongo_client.betfair_odds
    col = mongo_db.bf_events

    return col


def create_bkp_connection():
    password = urllib.parse.quote_plus(os.environ.get('MONGO_PASSWORD'))
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb+srv://joao:%s@maincluster-he8du.gcp.mongodb.net/test?retryWrites=true&w=majority" % password)
    mongo_db = mongo_client.betfair_bkp
    col = mongo_db.odds_bkp

    return col


async def process_all_items(main_db_collection, bkp_db_collection):
    cursor = main_db_collection.find({})

    async for document in cursor:
        print("Jogo consultado: {}".format(document['markets']['eventName']))

        if arrow.get(document['markets']['marketStartTime']) < arrow.utcnow():
            saved_match = await bkp_db_collection.update_one({
                'event_id': document['event_id']},
                {'$set': document},
                upsert=True
            )
            print("Salvo: {event_name} / {date}"
                  .format(event_name=document['markets']['eventName'],
                          date=document['markets']['marketStartTime'])
                  )

            deleted_match = await main_db_collection.delete_one({'_id': document['_id']})
            print("Deletado do main: {event_name} / {date}"
                  .format(event_name=document['markets']['eventName'],
                          date=document['markets']['marketStartTime']))


if __name__ == "__main__":
    main()
