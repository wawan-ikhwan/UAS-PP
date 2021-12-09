from socket import AF_INET, SOCK_STREAM, SO_REUSEADDR,SOL_SOCKET, timeout, socket
from threading import Thread
from time import sleep
import pandas as pd
import os
import glob

IP,PORT=('0.0.0.0',56322) # Environtment Config, edit terserah user

clients=[] #clients[posisisKlien][1=(ip,port)][0=ip,1=ports]
errors=(ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, TimeoutError, timeout)

s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Mencegah OSError
s.bind((IP,PORT))
s.listen()

# ========================================THREAD SERVER===============================
def sebarkanPesan(pesan,user='SERVER'): # Fungsi dimana server akan menyebarkan pesan ke semua client
  msg=user.ljust(15)+': '+pesan
  print('\r'+msg)
  for c in clients:
    try:
      c[0].settimeout(1)
      c[0].send(('\r'+msg).encode())
    except errors:
      clients.remove(c)

def serverInput(): # Fungsi dimana server dapat broadcast pesan
  global interupsi
  while not interupsi:
    sleep(0.1)
    serverInp=input()
    print ('\033[A                                                  \033[A') # clear last line
    if serverInp == '!cek':
      sebarkanPesan('Mengecek client yang online!')
      printClients('Online Clients',clients)
    elif serverInp == '!keluar':
      interupsi=True
      print('keluar')
    elif serverInp == '!splitWL':
      splitWL(len(clients)) # splitWL berdasarkan banyak clients
      #splitWL(3)
      sebarkanPesan('Server membelah wordlist!')
    elif serverInp == '!combineHasil':
      combineHasil('./wordlist/destination')
      sortHasil('./wordlist/destination')
      sebarkanPesan('Server menggabungkan hasil dan menyortir hasil!')
    else:
      sebarkanPesan(serverInp)

def serverAccept(): # Fungsi dimana server dapat menerima sambungan koneksi
  global interupsi
  while not interupsi:
    sleep(0.1)
    try:
      s.settimeout(1)
      clients.append(s.accept())
      sebarkanPesan(str(clients[-1][1]) + ' telah terhubung!\n'+'sessID='+str(len(clients)))
    except errors:
      pass

def serverReceive(): # Fungsi dimana server dapat menerima pesan
  global interupsi
  global clients
  while not interupsi:
    sleep(0.1)
    for c in clients:
      try:
        try:
          c[0].settimeout(1)
          pesan=c[0].recv(1024).decode()
          if len(pesan) > 0: # Jika pesan ada isi
            if pesan == '!put':
                sebarkanPesan(pesan,user=c[1][0])
            else:
              sebarkanPesan(pesan,user=c[1][0])
          else:
            clients.remove(c)
        except timeout:
          pass
      except errors:
        clients.remove(c)
# ========================================================================================

def printClients(judul,data):
  print()
  print(judul.center(50,'='))
  for i,d in enumerate(data):
    print(str(i)+'.',str(d[1]).ljust(46),end='|\n')
  print('='*50)

def splitWL(belah):
  wordlist=open('./wordlist/source/kota-kabupaten.txt','r').read().splitlines()
  banyakBaris=len(wordlist)
  jarakBaris=range(0,banyakBaris,banyakBaris//belah)
  lJarakBaris=list(jarakBaris)
  lJarakBaris.append(banyakBaris)
  print('Jarak baris:',lJarakBaris)
  deleteAllFilesInFolder('./wordlist/splitted')
  deleteAllFilesInFolder('./wordlist/destination')
  for pointer in range(len(jarakBaris)):
    namaFile=str(pointer+1)+'.txt'
    buffLines=wordlist[lJarakBaris[pointer]:lJarakBaris[pointer+1]]
    open('./wordlist/splitted/'+namaFile,'w').write('\n'.join(buffLines))

def combineHasil(path):
  open(path+'/hasil.csv','w').write('kota,trend\n')
  files = glob.glob(path+'/*')
  for f in files:
    if '.avg' in f:
      open(path+'/hasil.csv','a').write(open(f,'r').read())

def sortHasil(path):
  df=pd.read_csv(path+'/hasil.csv')
  df.sort_values(by=["trend"],ascending=False).to_csv(path+'/sortedHasil.csv',index=False)

def deleteAllFilesInFolder(path): # PERINGATAN: GUNAKAN SECARA HATI-HATI!
  files = glob.glob(path+'/*')
  for f in files:
      os.remove(f)

if __name__=='__main__':
  print('\rServer berjaland pada',IP,':',PORT,'\n')
  interupsi=False
  threadServerInput=Thread(target=serverInput,args=()) # digunakan untuk mengirim input ke semua clients
  threadServerAccept=Thread(target=serverAccept,args=())
  threadServerReceive=Thread(target=serverReceive,args=())
  threadServerInput.start()
  threadServerAccept.start()
  threadServerReceive.start()
  try:
    while True and not interupsi: sleep(1) # Menunggu interupsi
  except KeyboardInterrupt:
    interupsi=True
  threadServerInput.join()
  threadServerAccept.join()
  threadServerReceive.join()
  s.close()
  print('Server dimatikan!')

