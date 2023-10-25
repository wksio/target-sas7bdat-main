#!/usr/bin/env python3
import saspy
import argparse
import io
import os
import sys
import json
import threading
import http.client
import urllib
from datetime import datetime
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections.abc as collections
else:
    import collections
import pkg_resources
from jsonschema.validators import Draft4Validator
import singer
import pandas as pd
import pathlib
import pythoncom

logger = singer.get_logger()

def emit_state(state):
    if state is not None:
        line = json.dumps(state)
        logger.debug('Emitting state {}'.format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()

def flatten(d, parent_key='', sep='__'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v) if type(v) is list else v))
    return dict(items)
        
def persist_messages(config,messages):
    state = None
    schemas = {}
    key_properties = {}
    headers = {}
    validators = {}
    try:
        pythoncom.CoInitialize()
        currentpath=str(pathlib.Path(__file__).parent.resolve())
        sascfg=os.path.join(currentpath,"sascfg.py")
        sas = saspy.SASsession(cfgfile=sascfg,user=config['user'], pw=config['password'])
    except:
        logger.error("Unsuccessful connection to SAS or credential error")
        raise
    now = datetime.now().strftime('%Y%m%dT%H%M%S')
    df=pd.DataFrame()
    for message in messages:
        try:
            o = singer.parse_message(message).asdict()
        except json.decoder.JSONDecodeError:
            logger.error("Unable to parse:\n{}".format(message))
            raise
        message_type = o['type']
        if message_type == 'RECORD':
            if o['stream'] not in schemas:
                raise Exception("A record for stream {}"
                                "was encountered before a corresponding schema".format(o['stream']))

            validators[o['stream']].validate(o['record'])

            filename = config['tablename']
            flattened_record = flatten(o['record'])
            headers[o['stream']] = flattened_record.keys()
            if df.empty:
                df=pd.DataFrame.from_records([flattened_record],columns=list(flattened_record.keys()))
            else: 
                df2=pd.DataFrame.from_records([flattened_record],columns=list(flattened_record.keys())) 
                df=pd.concat([df,df2],axis=0) 
                 
            state = None
        elif message_type == 'STATE':
            logger.debug('Setting state to {}'.format(o['value']))
            state = o['value']
        elif message_type == 'SCHEMA':
            stream = o['stream']
            schemas[stream] = o['schema']
            validators[stream] = Draft4Validator(o['schema'])
            key_properties[stream] = o['key_properties']
        else:
            logger.warning("Unknown message type {} in message {}"
                            .format(o['type'], o))
    sas.saslib(config['libname'], path=config['libpath'])
    sas.dataframe2sasdata(df=df, table=filename, libref=config['libname']) 

    return state


def send_usage_stats():
    try:
        version = pkg_resources.get_distribution('target-csv').version
        conn = http.client.HTTPConnection('collector.singer.io', timeout=10)
        conn.connect()
        params = {
            'e': 'se',
            'aid': 'singer',
            'se_ca': 'target-sas',
            'se_ac': 'open',
            'se_la': version,
        }
        conn.request('GET', '/i?' + urllib.parse.urlencode(params))
        response = conn.getresponse()
        conn.close()
    except:
        logger.debug('Collection request failed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file')
    args = parser.parse_args()

    if args.config:
        with open(args.config) as input:
            config = json.load(input)
    else:
        config = {}

    if not config.get('disable_collection', False):
        logger.info('Sending version information to singer.io. ' +
                    'To disable sending anonymous usage data, set ' +
                    'the config parameter "disable_collection" to true')
        threading.Thread(target=send_usage_stats).start()

    input_messages = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    state = persist_messages(config, input_messages)
        
    emit_state(state)
    logger.debug("Exiting normally")


if __name__ == '__main__':
    main()
