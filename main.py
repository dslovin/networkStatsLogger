#crontab -e */10 * * * *
import speedtest
import ifcfg
import iwlib
import json
import requests
import argparse, sys
from datetime import datetime
from google.cloud import storage






def run_speedtest():
    servers = []
    threads = None
    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads)
    s.results.share()
    return s.results.dict()
    
def get_ifcfg():
    return ifcfg.interfaces()
    
def get_iwlib():
    stats = iwlib.get_iwconfig('wlan0')
    for s in stats:
        stats[s]=str(stats[s])
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name',help="Name of Device")
    parser.add_argument('-b', '--bucket',help="GCP Bucket")
    parser.add_argument('-k', '--key',help="Key with bucket write privileges")
    args = parser.parse_args()
    name = args.name
    bucket = args.bucket
    key = args.key
    print(f'Name:{name}')
    print(f'Bucket:{bucket}')
    print(f'KeyPath:{key}')           
    timestamp = str(datetime.now())        
    js = json.dumps({'id':name,'timestamp':timestamp,'speedtest':run_speedtest(),'ifcfg':get_ifcfg(),'iwcfg':get_iwlib()})
    print(f'Original:{js}')
    storage_client = storage.Client.from_service_account_json(key)
    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(f'{name}/{timestamp}.json')
    blob.upload_from_string(js,content_type='application/json')

if __name__ == "__main__":
    main()