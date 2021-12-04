from socket import AF_INET, SOCK_STREAM, SO_REUSEADDR,SOL_SOCKET, timeout, socket
from threading import Thread
from time import sleep

IP,PORT=('0.0.0.0',80) # Environtment Config, edit terserah user

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

if __name__=='__main__':
  print('\rServer berjalan pada',IP,':',PORT,'\n')
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

