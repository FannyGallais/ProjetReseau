
import socket
import threading
import time
import sys



class livreur:
	
	def __init__(self,num):
		self.num=num #Chaque livreur a un numero
		self.occupe=False #Un livreur peut etre occupe ou non par une livraison

	def __repr__(self):
		if self.occupe==False:
			return "Livreur"+str(self.num)+" : disponible\n"
		else :
			return "Livreur"+str(self.num)+" : occupe\n"


restaurant = []
for i in xrange(10):
	restaurant.append(livreur(i+1))


restaurant[0].occupe=True



#############################################################################
#								PARTIE SERVEUR								#
#############################################################################
listeClient=[]

def f_thread(clisock):
    loopEnd = True
    t=0
    #On cherche le premier livreur disponible:
    num_livreur=0 
    while restaurant[num_livreur].occupe==True:
		num_livreur +=1
		
    restaurant[num_livreur].occupe=True
    time=0
       
	
  
    while loopEnd:
        data = clisock.recv(2048)
        if t==0:
			print data
			num = data[6]
        clisock.send(data)
        t+=1
        time+=1
        print time
	
	if time>100000:
	   print "Le client"+num+" a ete livre par le livreur"+str(restaurant[num_livreur].num)
	   restaurant[num_livreur].occupe=False
	   clisock.send("fin")
	   clisock.shutdown(0)
	   listeClient.remove(clisock)
	   loopEnd = False

	
	


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('',8001))
sock.listen(5)
while True:
	clisock, addr = sock.accept()
	listeClient.append(clisock)
	print "Un client a passe commande"
	t = threading.Thread(target=f_thread, args=(clisock,))
	t.start()

