#!/usr/bin/python2.6
#-*- coding: utf-8 -*-

import socket
import struct
import errno
import datetime
import json 
import configuration
import re

### "Processed 0 Failed 1 Total 1 Seconds spent 0.000048"
RESP_RE = re.compile("""^Processed\s+(\d+)\s+Failed\s+(\d+)\s+Total\s+(\d+).*$""")

HEADER = 'ZBXD\x01'
CONFIG = '/etc/zabbix_server.conf'

def prepare_data(body):
	l = len(body)
	padding = '\x00\x00\x00\x00'
	if l >= 2 << 31:
		padding = ''
	return HEADER + struct.pack('<I',l) + padding + body

def send_to_server(host, port, data, conn_timeout = 1, read_timeout = 3):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(conn_timeout)
	try:
		s.connect((host, port))
	except Exception, ex:
		if ex.errno == -2:
			msg = "Could not resolve %s" % host
		else:
			msg = "Could not connect to %s:%s - %s" % (host, port, str(ex))
		return {
			"status": "failure",
			"error": msg
		}	
	s.settimeout(read_timeout)
	try:
		s.send(data)
		hdr = s.recv(5)
		len = s.recv(8)
		all = s.recv(1000)
	except Exception, ex:
                if ex.errno == -2:
                        msg = "Could not resolve %s" % host
                else:
                        msg = "Could not send data to %s:%s - %s" % (host, port, str(ex))
                return {
                        "status": "failure",
                        "error": msg
                }
	s.close()
	return process_server_response(all)

def process_server_response(resp):
	data = json.loads(resp)
	mt = re.match(RESP_RE,data['info'])
	if mt == None:
		return None
	return {
		"status": data['response'],
		"processed": mt.group(1),
		"failed": mt.group(2),
		"total": mt.group(3)
	}

def get_timestamp():
	return int(datetime.datetime.now().strftime("%s"))

def get_configuration():
	cfg = configuration.parse(CONFIG)
	host = cfg['host'][0]
	port = int(cfg['port'][0])
	return {
		"host": host,
		"port": port
	}

def transform_data(data, host):
	ts = get_timestamp()
	if host == None:
		host = socket.gethostname()
	res = {
		"request":"agent data",
		"data": [],
		"clock": ts
	}
	i = 0
	for key, val in data.iteritems():
		res['data'].append({
			"host": host,
			"key": key,
			"value": val,
			"clock": ts
		})
		i += 1
	if i == 0:
		return None
	return res

#dict key_val
def send_data(key_val, host=None):
	data = transform_data(key_val,host)
	if data == None:
		return {
			"status": "failure",
			"error": "empty data"
		}
	body = prepare_data(json.dumps(data))
	try:
		cfg = get_configuration()
		return send_to_server(cfg['host'], cfg['port'], body)
	except Exception, ex:
		print str(ex)
		return None

if __name__ == "__main__":
	CONFIG = './zabbix_server.conf'
	print json.dumps(send_data({'appstats.cache_misses': 1}))

