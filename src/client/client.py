from socket import socket
from threading import Thread
import time
import os
import glob
import requests
from pytrends.request import TrendReq
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

relativePath=os.path.dirname(os.path.realpath(__file__))+'/'
os.chdir(relativePath)
os.system('mkdir WLpart')
os.system('mkdir CSVpart')
os.system('mkdir AVGpart')

interupsi=False
IP,PORT=('27.112.79.120',12345)
#IP,PORT=('127.0.0.1',12345)

s=socket()
s.connect((IP,PORT))

# ======================THREAD CLIENT==================================
sessID=None
def clientReceive():
  global relativePath
  global interupsi
  global sessID
  while not interupsi:
    time.sleep(0.1)
    try:
      s.settimeout(1)
      if not interupsi:
        buffer=s.recv(1024).decode()
        print(buffer)
        if sessID is None and 'sessID=' in buffer:
          setupFolder()
          sessID=buffer[buffer.rfind('=')+1:] #filter char '=' karena didapat dari pesan server ketika client pertama kali masuk
          open(relativePath+'./sessID.txt','w').write(sessID)
        elif '!get' in buffer:
          print('Sedang mengambil wordlist parsial')
          getData()
          print('Sukses mengambil wordlist parsial')
        elif '!fetch' in buffer:
          print('Sedang mengambil trend parsial')
          fetching(sessID)
          print('sukses mengambil trend parsial')
        elif '!put' in buffer:
          print('Sedang mengupload hasil parsial')
          putData(sessID+'.avg')
          print('sukses mengupload hasil parsial')
    except:
      pass
  exit()

def clientSend():
  global relativePath
  global interupsi
  global sessID
  while not interupsi:
    time.sleep(0.1)
    pesan=input()
    print ('\033[A                                              \033[A') # clear last line
    if pesan == '!keluar':
      interupsi=True
    elif pesan == '!put':
      putData(sessID+'.avg')
    elif pesan == '!get':
      getData()
    elif pesan == '!fetch':
      fetching(sessID)
    s.send(pesan.encode())
  exit()
# =============================================================

def fetching(sessID,sleepTime=5):
  global relativePath
  wl=open(relativePath+'./WLpart/'+sessID+'.txt').read().splitlines()
  banyakBaris=len(wl)-1
  trend=TrendReq(hl='id',timeout=(10,25),retries=2, backoff_factor=0.1, requests_args={'verify':False})
  for i in range(banyakBaris):
    target=wl[i]
    kw_list = [target]
    trend.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='ID', gprop='')
    df=trend.interest_over_time()
    df.to_csv(relativePath+'./CSVpart/'+target+'.csv')
    avg=target+','+str(int(df.mean(numeric_only=True)))
    print(avg+str(' | ')+str(i)+'/'+str(banyakBaris)+'\n')
    open(relativePath+'./AVGpart/'+sessID+'.avg','a+').write(avg+'\n')
    time.sleep(sleepTime)

def putData(fileName):
  global relativePath
  headers = {'Content-Type': 'text/plain'}
  url='http://27.112.79.120:8000/'+fileName
  r = requests.put(url, data=open(relativePath+'./AVGpart/'+fileName, 'rb'),headers=headers)

def getData():
  global sessID
  global relativePath
  url = 'http://27.112.79.120:8000/splitted/'+sessID+'.txt'
  r = requests.get(url)
  open(relativePath+'./WLpart/'+sessID+'.txt', 'wb').write(r.content)

def deleteAllFilesInFolder(path): # PERINGATAN: GUNAKAN SECARA HATI-HATI!
  global relativePath
  files = glob.glob(relativePath+path+'/*')
  for f in files:
      os.remove(f)

def setupFolder():
  deleteAllFilesInFolder('./WLpart')
  deleteAllFilesInFolder('./AVGpart')
  deleteAllFilesInFolder('./CSVpart')

if __name__=='__main__':
  threadClientReceive=Thread(target=clientReceive,args=())
  threadClientSend=Thread(target=clientSend,args=())
  threadClientReceive.start()
  threadClientSend.start()
  try:
    while True and not interupsi: time.sleep(1) # Menunggu interupsi
  except KeyboardInterrupt:
    interupsi=True
  print('Anda keluar!')
  threadClientReceive.join()
  threadClientSend.join()
  s.close()