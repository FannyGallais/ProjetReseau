
import socket
import threading
import time
import sys
verrou=threading.Lock()



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
for i in xrange(5):
	restaurant.append(livreur(i+1))


restaurant[0].occupe=False
restaurant[1].occupe=False
restaurant[2].occupe=True
restaurant[3].occupe=True
restaurant[4].occupe=True


def livreur_dispo():
	id_livreur=0 
	while restaurant[id_livreur].occupe==True:
		id_livreur +=1
		if id_livreur>=len(restaurant): #Si aucun livreur n'est libre
			return "wait"
	print " on utilise le livreur ",id_livreur		
	return id_livreur


"""
def livreur_dispo():
	nb_livreur=0 
	for i in range(len(restaurant)):
		if restaurant[i].occupe==True :
			nb_livreur+=1
	return nb_livreur		

"""	


#############################################################################
#								PARTIE SERVEUR								#
#############################################################################
listeClient=[]

def f_thread(clisock):

	loopEnd = True
	t=0
	#On cherche le premier livreur disponible:
	waiting_time=0
	while livreur_dispo()=="wait": #On attend qu'un livreur soit disponible
		waiting_time+=1
		id_livreur=livreur_dispo()
	id_livreur=livreur_dispo()
	restaurant[id_livreur].occupe=True
	num_livreur=restaurant[id_livreur].num
	time=0
       
	
  
	while loopEnd:
		data = clisock.recv(2048)
		if t==0:
			print data
			num = data[6]
			clisock.send(str(num_livreur)) #On envoie le numero du livreur au client
			
		clisock.send(data)
		t+=1
		time+=1


		if time>50000:
		   print "Le client"+num+" a ete livre par le livreur"+str(num_livreur)+" apres un temps d'attente de "+str(waiting_time)
		   ecriture(num,str(num_livreur),str(waiting_time))
		   restaurant[id_livreur].occupe=False
		   if waiting_time!=0: #Pour signaler qu'il y a eu de l'attente a la partie client
			   clisock.send("fin_attente")
		   else:
				clisock.send("fin")
		   clisock.shutdown(0)
		   listeClient.remove(clisock)
		   loopEnd = False



fichier=open('test.txt','w')
verrou1=threading.Lock()

def ecriture(client,livreur,attente):
	verrou1.acquire()
	fichier.write("Le client "+client+"	a ete livre par :	"+livreur+ "    Attente :"+attente+"\n")
	verrou1.release()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('',8001))
sock.listen(5)
while True:
	clisock, addr = sock.accept()
	listeClient.append(clisock)
	print "Un client a passe commande"
	
	"""
	verrou.acquire()
	nb_livreur=livreur_dispo()
	#if nb_livreur==5: # Ces deux lignes font beuger le code 
	#	print "Attente d'un livreur"
	while (nb_livreur>4):
		nb_livreur=livreur_dispo()

		
	verrou.release()
	"""	
	t = threading.Thread(target=f_thread, args=(clisock,))
	t.start()
	
	

fichier.close()
