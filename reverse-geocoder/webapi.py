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

gsi_endpoint = {
     'revgeocode':'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress',
     'elevation':'https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php'
  }

def lookup_muniCode(m):
     conn = sqlite3.connect('munitable.db')
     cur = conn.cursor()

     try:
          query = 'select * from muni where muniCd = ?'
          cur.execute(query, (m, ))
          r = cur.fetchone()
          if r:
               (_, pref, city, jcc, jcc_text, jcg, jcg_text) = r
               ty = 'JCC'
               city = re.sub(r'(.+)\(.+\)',r'\1',city)
               jcc_text = re.sub(r'(.+)\(.+\)',r'\1',jcc_text)
               if jcg != '':
                    city = jcg_text + '郡' + city
                    ty = 'JCG'
          else:
               raise Exception
          
          conn.close();

          if ty == 'JCC':
               res = { 'pref': pref, 'addr2': city, 'addr1': '','type': ty,
                       'jcc': jcc, 'jcc_text': jcc_text
               }
          else:
               res = { 'pref': pref, 'addr2': city, 'addr1': '','type': ty,
                       'jcg': jcg, 'jcg_text': jcg_text
               }

          return res
     
     except Exception as err:
          conn.close()
          return {}

def rev_geocode(lat,lng,elev):
     pos = '?lat=' + lat + '&lon=' + lng
     rev_uri = gsi_endpoint['revgeocode']+ pos 
     elev_uri = gsi_endpoint['elevation']+ pos + '&outtype=JSON'
     try:
          r_get = requests.get(rev_uri)
          if r_get.status_code == 200:
               res = r_get.json()
               if res:
                    r = lookup_muniCode(str(int(res['results']['muniCd'])))
                    r['addr1'] = res['results']['lv01Nm']
               else:
                    raise Exception
               if elev:
                    r_get = requests.get(elev_uri)
                    if r_get.status_code == 200:
                         res = r_get.json()
                         if res:
                              r['elevation'] = res['elevation']
                              r['hsrc'] = res['hsrc']
               return r
          else:
               raise Exception
     except Exception as err:
          return {'errors':'parameter out of range'}

res = {'Errors': ''}
form = cgi.FieldStorage()
app = form.getvalue('arg0',None)
func = form.getvalue('arg1',None)

res['errors'] = 'Invalid parameters'

if app == 'reverse-geocoder':
     if 'LonLatToAddress' in func:
          if func == 'LonLatToAddressElev':
               elev = True
          else:
               elev = False
               
          if 'lat' in form and 'lon' in form:
               lat = form['lat'].value
               lng = form['lon'].value
               res = rev_geocode(lat, lng, elev)
               res['errors'] = 'OK'
               
print('Content-Type:application/json\n\n')
print(json.dumps(res))

