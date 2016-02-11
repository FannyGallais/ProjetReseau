
import socket
import threading
import random
import time
import sys
from Tkinter import *

#########################################################################################
#								PARTIE INTERFACE DU SERVEUR								#
#########################################################################################

class Interface:

	def __init__(self,chiffre, temps_moyen_attente) :

		self.fenetre = Tk()
		self.fenetre.geometry("500x500")

		self.fenetre.title("BILAN DE LA SOIREE")

		self.panel = PanedWindow(self.fenetre,orient=VERTICAL,height=750,width=1000)
		self.panel.pack()
		self.var = StringVar()
		self.situation = Label(self.fenetre,textvariable=self.var,height=10)
		self.var.set("Chiffre d'affaire du jour: "+str(chiffre)+ " euros \n Temps moyen d'attente: "+"{0:.2f}".format(temps_moyen_attente)+"s")
		self.panel.add(self.situation)
		self.quitter=Button(self.fenetre,text="Quitter",command=self.b_quitter)
		self.panel.add(self.quitter)
		self.bilan=Button(self.fenetre,text="Bilan",command=self.b_bilan)
		self.panel.add(self.bilan)
		self.text = Text()
		self.panel.add(self.text)
		
		
	def b_quitter(self):
		sys.exit()
	def b_bilan(self):
		self.text.insert(1.,open("Commandes.txt",'r').read())
		
		
		
#############################################################################
#								CLASSE LIVREUR								#
#############################################################################
class livreur:
	
	def __init__(self,num):
		self.num=num #Chaque livreur a un numero
		self.occupe=False #Un livreur peut etre occupe ou non par une livraison

	def __repr__(self):
		if self.occupe==False:
			return "Livreur"+str(self.num)+" : disponible\n"
		else :
			return "Livreur"+str(self.num)+" : occupe\n"


#Creation de l'enemble des livreurs
restaurant = []
for i in xrange(5):
	restaurant.append(livreur(i+1))


#Defenition du statut de chaque livreur
restaurant[0].occupe=True
restaurant[1].occupe=False
restaurant[2].occupe=False
restaurant[3].occupe=True
restaurant[4].occupe=True


#Cette fonction renvoie wait si tous les livreurs sont occupes, l'identifiant du premier livreur disponible sinon
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
listeClient=[] #Cette liste stocke tous les clients qui se sont connectes
listeClient2=[] #Cette liste stocke les clients en cours de livraison
threads=[] #Cette liste stocke les threads

max_commande=4 #Nombre max de comandes avant fermeture du serveur

liste_prix=[] #Pour stocker les prix des differntes commandes
liste_temps_attente=[] #Pour stocker les temps d'attente des differents clients


def f_thread(clisock):
	loopEnd = True
	t=0
	
	start_time=time.time() #Initialisation du decompte du temps
	
	#On cherche le premier livreur disponible:
	waitServeur=0
	
	while livreur_dispo()=="wait": #On attend qu'un livreur soit disponible
		waitServeur +=1
		
	id_livreur=livreur_dispo() #livreur attitre a la livraison
	restaurant[id_livreur].occupe=True
	num_livreur=restaurant[id_livreur].num
	print "On utilise le livreur ",num_livreur
	
  
	while loopEnd:
		data = clisock.recv(2048)
		if t==0:
			print data
			num = data[6] #numero du client
			stock=data.split("(")[1]
			prix=int(stock.split("e")[0]) #prix du menu
			clisock.send(str(num_livreur)) #On envoie le numero du livreur au client
			
		clisock.send(data)
		t+=1
		
		time.sleep(random.randint(5,20)) #Le temps varie aleatoirement d'une livraison a l'autre
		waiting_T=time.time()-start_time
		
		print "Le client"+num+" a ete livre par le livreur"+str(num_livreur)+" apres un temps d'attente de "+("{0:.2f}".format(waiting_T))+str("s")
		
		liste_prix.append(prix)
		liste_temps_attente.append(waiting_T)
		restaurant[id_livreur].occupe=False #Le livreur est de nouveau disponible
		
		ecriture(num,str(num_livreur),"%.2f" %waiting_T) #on laisse une trace de la commande dans le fichier commande.txt
	
		clisock.send("Temps d'attente : %.2f" %waiting_T) #On informe le client de son temps d'attente
		
		#On retire ce client qui a ete livre de la liste
		listeClient2.remove(clisock)
		
		if waitServeur!=0: #Pour signaler qu'il y a eu de l'attente avant d'obtenir un livreur a la partie client
			clisock.send("fin_attente")
		else:
			clisock.send("fin")
			
		clisock.shutdown(0)
		
		loopEnd = False



fichier=open('Commandes.txt','w') #Ce fichier garde une trace des commandes passees
verrou1=threading.Lock() #Pour eviter les conflits d'ecriture dans le fichier


def ecriture(client,livreur,attente):
	verrou1.acquire()
	fichier.write("Le client "+client+"	a ete livre par le livreur "+livreur+ "    Attente :"+attente+"\n")
	verrou1.release()



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('',8001))
sock.listen(5)
while True:
	clisock, addr = sock.accept()
	listeClient.append(clisock)
			
	#Si on a atteint le maximum de commande, le client ne peux plus commander
	if len(listeClient)>max_commande:
		clisock.send("bloque")
		if len(listeClient2)==0 :	
			break	
	
	listeClient2.append(clisock)

	print "Un client a passe commande"
	
	t = threading.Thread(target=f_thread, args=(clisock,))
	threads.append(t)
	t.start()
	
	#Lorsque l'on a atteint le maximum de commandes, on doit faire en sorte que les livraisons se terminent avant de fermer le serveur
	if len(listeClient)>max_commande-1: 
		
		#On termine d'abord la commande du dernier client qui s'est connecte
		t.join()
		
		#Il faut traiter le cas ou d'autres clients que le dernier n'ont pas termine (c'est a dire quand listeClient2 contint des elements)
		if len(listeClient2)!=0:
			print "Il reste "+str(len(listeClient2))+" client(s)"
			
			index=[] #Liste des index des clients toujours en cours de livraison
			
			for i in xrange(len(listeClient2)):
				for j in xrange(len(listeClient)):
					if listeClient2[i]==listeClient[j]:  
						index.append(j)
						
			for i in xrange(len(index)):
				threads[index[i]].join() #on met un join sur chaque client qui n'a pas fini 
				
		fichier.close()
	
	#Si plus aucun client n'est en cours de commande, on ferme le serveur	
	if len(listeClient2)==0 :	
		break	
	


# Une fois que le maximum de commande est atteint, les clients ne peuvent plus se connecter, un bilan s'affiche a l'ecran

print "Fin du service"
sock.close() #Ferme le serveur et empeche les client de se connecter
chiffre = sum(liste_prix)
temps_moyen_attente=sum(liste_temps_attente)/len(liste_temps_attente)
I=Interface(chiffre, temps_moyen_attente)
I.fenetre.mainloop()
