#!/usr/bin/env python3
# coding:utf-8
import csv
import json
import sqlite3
import urllib

with open('town-gun-utf8.csv') as f:
     reader = csv.reader(f)
     town = [row for row in reader]

conn = sqlite3.connect('munitable.db')
cur = conn.cursor()
cur_jcc = conn.cursor()
cur2 = conn.cursor()

def lookup_from_town(t):
     for row in town:
          if t in row[0]:
               return (row[1],row[2])
     return ("","")
     
def main():
     query = 'select * from muni'
     for (municd,name1,name2,jcc,_,jcg,_) in cur.execute(query):
          n = name2.split(' ')
          nm = n[0].replace(' ','')
          jcc_text = ''
          jcc = ''
          (jcg_text,jcg) = (lookup_from_town(nm))
          if jcg == "":
               query = 'select * from jcc where Name2 = ?'
               cur_jcc.execute(query, (nm, ))
               r = cur_jcc.fetchall()
               if r:
                    for (code,_,name,_) in r:
                         jcc_text = name
                         jcc = code
               else:
                    print("Error "+nm)
                    return
          else:
               jcg_text = jcg_text + '郡'
          query = 'update muni set JCCCd = ?, JCC_text = ?, JCGCd = ? ,JCG_text = ? where muniCd =  ?'
          try:
               cur2.execute(query,(jcc, jcc_text, jcg, jcg_text , municd))
               conn.commit()
          except Exception as err:
               print(err)
               return
     conn.close()
     
main()
                       
