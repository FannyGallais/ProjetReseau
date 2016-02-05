
import socket
import threading
import time
import sys
from Tkinter import *

class Interface:

	def __init__(self) :

		self.fenetre = Tk()
		self.fenetre.geometry("500x500")

		self.fenetre.title("BILAN DE LA SOIREE")

		self.panel = PanedWindow(self.fenetre,orient=VERTICAL,height=750,width=1000)
		self.panel.pack()
		self.var = StringVar()
		self.situation = Label(self.fenetre,textvariable=self.var,height=10)
		self.var.set("Voici le bilan de la soiree")
		self.panel.add(self.situation)
		self.quitter=Button(self.fenetre,text="Quitter",command=self.b_quitter)
		self.panel.add(self.quitter)
	
	def b_quitter(self):
		sys.exit()

		

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
	return id_livreur



#############################################################################
#								PARTIE SERVEUR								#
#############################################################################
listeClient=[]
max_commande=5

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
	print " on utilise le livreur ",num_livreur
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
		   loopEnd = False



fichier=open('Commandes.txt','w')
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
	t = threading.Thread(target=f_thread, args=(clisock,))
	t.start()
	t.join()
	if len(listeClient)>max_commande-1: break

sock.close() #Empeche les client de se connecter
print "Fin"
I=Interface()
I.fenetre.mainloop()
fichier.close()
