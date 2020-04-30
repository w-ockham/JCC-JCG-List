#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import cgi
import csv
import io
import json
import re
import sqlite3
import sys
import requests

gsi_endpoint = 'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress'

def lookup_muniCode(m):
     conn = sqlite3.connect('munitable.db')
     cur = conn.cursor()

     try:
          query = 'select * from muni where muniCd = ?'
          cur.execute(query, (m, ))
          r = cur.fetchone()
          if r:
               (_, pref, city, jcc, jcg) = r
               jccName = ''
               jcgName = ''
               ty = ''
               city = re.sub(r'(.+)\(.+\)',r'\1',city)
               if jcc != '':
                    query = 'select * from jcc where JCC = ?'
                    cur.execute(query, (jcc, ))
                    (_, _, jccName, _ ) = cur.fetchone()
                    jccName = re.sub(r'(.+)\(.+\)',r'\1',jccName)
                    ty = 'JCC'
               elif jcg != '':
                    query = 'select * from jcg where JCG = ?'
                    cur.execute(query, (jcg, ))
                    (_, _, jcgName, _ ) = cur.fetchone()
                    city = jcgName + '郡' + city
                    ty = 'JCG'
          else:
               raise
          
          conn.close();

          if ty == 'JCC':
               res = { 'pref': pref, 'addr2': city, 'addr1': '','type': ty,
                       'jcc': jcc, 'jcc_text': jccName,
               }
          else:
               res = { 'pref': pref, 'addr2': city, 'addr1': '','type': ty,
                       'jcg': jcg, 'jcg_text': jcgName
               }

          return res
     
     except Exception as err:
          conn.close()
          return {}

def rev_geocode(lat,lng):
     try:
          r_get = requests.get(gsi_endpoint + '?lat=' + lat + '&lon=' + lng)
          if r_get.status_code == 200:
               res = r_get.json()
               if res:
                    r = lookup_muniCode(str(int(res['results']['muniCd'])))
                    r['addr1'] = res['results']['lv01Nm']
                    return r
               else:
                    raise
          else:
               raise
     except Exception as err:
          return {'errors':'parameter out of range'}

res = {'Errors': ''}
form = cgi.FieldStorage()
app = form.getvalue('arg0',None)
func = form.getvalue('arg1',None)

res['errors'] = 'Invalid parameters'

if app == 'reverse-geocoder':
     if func == 'LonLatToAddress':
          if 'lat' in form and 'lon' in form:
               lat = form['lat'].value
               lng = form['lon'].value
               res = rev_geocode(lat,lng)
               res['errors'] = 'OK'
               
print('Content-Type:application/json\n\n')
print(json.dumps(res))

