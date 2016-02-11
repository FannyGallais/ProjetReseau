
import socket
import threading
import random
import time
import sys
from Tkinter import *

class Interface:

	def __init__(self,chiffre, temps_moyen_attente,sock) :

		self.fenetre = Tk()
		self.fenetre.geometry("500x500")

		self.fenetre.title("BILAN DE LA SOIREE")

		self.panel = PanedWindow(self.fenetre,orient=VERTICAL,height=750,width=1000)
		self.panel.pack()
		self.var = StringVar()
		self.situation = Label(self.fenetre,textvariable=self.var,height=10)
		self.var.set("Chiffre d'affaire du jour: "+str(chiffre)+ " euros \n Temps moyen d'attente:" + str(temps_moyen_attente))
		self.panel.add(self.situation)
		self.quitter=Button(self.fenetre,text="Quitter",command=self.b_quitter)
		self.panel.add(self.quitter)
		self.bilan=Button(self.fenetre,text="Bilan",command=self.b_bilan)
		self.panel.add(self.bilan)
		self.text = Text()
		self.panel.add(self.text)
		
		self.serveur=sock
		
	def b_quitter(self):
		sys.exit()
	def b_bilan(self):
		self.text.insert(1.,open("Commandes.txt",'r').read())
		
		

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


restaurant[0].occupe=True
restaurant[1].occupe=False
restaurant[2].occupe=False
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
listeClient2=[]
threads=[]
max_commande=4 #Nombre max de comandes avant fermeture du serveur
liste_prix=[] #Pour stocker les prix des differntes commandes
liste_temps_attente=[]

def f_thread(clisock):
	loopEnd = True
	t=0
	#On cherche le premier livreur disponible:
	waitServeur=0
	start_time=time.time()
	while livreur_dispo()=="wait": #On attend qu'un livreur soit disponible
		waitServeur +=1
		id_livreur=livreur_dispo()
	id_livreur=livreur_dispo()

	restaurant[id_livreur].occupe=True
	num_livreur=restaurant[id_livreur].num
	print " on utilise le livreur ",num_livreur

  
  
	while loopEnd:
		data = clisock.recv(2048)
		if t==0:
			print data
			print str(num_livreur)
			num = data[6]
			stock=data.split("(")[1]
			prix=int(stock.split("e")[0]) #prix du menu
			clisock.send(str(num_livreur)) #On envoie le numero du livreur au client
			
		clisock.send(data)
		t+=1
		
		if len(listeClient)==4:
			time.sleep(5)
		else:
			time.sleep(random.randint(10,30)) 
		waiting_T=time.time()-start_time
		
		print "Le client"+num+" a ete livre par le livreur"+str(num_livreur)+" apres un temps d'attente de "
		print("{0:.2f}".format(waiting_T))+str("s")
		liste_prix.append(prix)
		liste_temps_attente.append(waiting_T)
		restaurant[id_livreur].occupe=False
		
		ecriture(num,str(num_livreur),"%.2f" %waiting_T) #on laisse une trace de la commande dans un fichier texte
	
		clisock.send("Temps d'attente : %.2f" %waiting_T)
		
		#on retire ce client qui a ete livre
		listeClient2.remove(clisock)
		
		#faire du menage ici
		if waiting_T!=0: #Pour signaler qu'il y a eu de l'attente a la partie client
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
	
	if len(listeClient)>max_commande:
		print "je dois etre bloque"
		clisock.send("bloque")
		if len(listeClient2)==0 :	
			break	
	
	#creation d'une deuxieme liste pour pouvoir garder seulement les clients en court de commande cf ligne 126/127
	listeClient2.append(clisock)


	print "Un client a passe commande"
	t = threading.Thread(target=f_thread, args=(clisock,))
	
	#liste de threads pour pouvoir utiliser join sur un un client cible
	threads.append(t)
	
	t.start()
	
	if len(listeClient)>max_commande-1: #probleme : si d'autres clients sont en train de commander ils ne peuvent pas finir leurs commandes
		
		#on doit d'abord finir le dernier client
		t.join()
		
		#cas ou il reste d'autres clients, autres que le dernier, en attente 
		print str(len(listeClient2))
		if len(listeClient2)!=0:
			print "ENCORE DES CLIENTS"
			"""
			listeClient3=[]
			for k in xrange(len(listeClient2)):
				listeClient3[k]=listeClient2[k]
			"""
			a=[]
			for i in xrange(len(listeClient2)):
				for j in xrange(len(listeClient)):
					if listeClient2[i]==listeClient[j]:  #on met un join sur le client qui n'a pas fini 
						print "ENCORE LE CLIENT ", str(j+1)
						a.append(j)
			for i in xrange(len(a)):
				threads[a[i]].join()
		fichier.close()
	


# Une fois que le maximum de commande est atteint, les clients ne peuvent plus se connecter, un bilan s'affiche a l'ecran

print "Fin"
sock.close() #Empeche les client de se connecter
chiffre = sum(liste_prix)
temps_moyen_attente=sum(liste_temps_attente)/len(liste_temps_attente)
I=Interface(chiffre, temps_moyen_attente,sock)
I.fenetre.mainloop()
