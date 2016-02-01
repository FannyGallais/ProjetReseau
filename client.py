import socket 
import select
import time
import sys
import signal
import random
from Tkinter import*



def run_client(num,I):
	I.chgt_situation("Traitement de la commande en cours\n En attente d'un livreur disponible")
	global stopLoop
	stopLoop=True
	try:

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(("",8001))
		t=0
		while stopLoop:
			msg ="client"+str(num)+" en attente pour un "+c
			s.send(msg)
			data = s.recv(255)
			if t==0:
				I.chgt_situation("Traitement de la commande en cours\n le livreur "+data[0]+" s'occupe de la livraison") #Pour savoir par quel livreur est pris en charge le client
			t+=1
			if data == "fin": 
				I.chgt_situation("Votre commande a bien ete livree\n Vous pouvez commander de nouveau ou quitter")
				stopLoop=False
			if data == "fin_attente": 
				I.chgt_situation("Votre commande a bien ete livree, nous nous excusons pour l'attente!\n Vous pouvez commander de nouveau ou quitter")
				stopLoop=False



	except socket.error, e:
			print "erreur dans l'appel a une methode de la classe socket: %s" % e
			sys.exit(1)
	finally:
		#s.shutdown(1)
		s.close()
		print "Le client a recu sa commande"
		
	
	
	

class Interface:

	def __init__(self, num_client) :

		self.fenetre = Tk()
		self.fenetre.geometry("500x500")

		self.fenetre.title("CLIENT "+str(num_client))

		self.panel = PanedWindow(self.fenetre,orient=VERTICAL,height=750,width=1000)
		self.panel.pack()
		self.var = StringVar()
		self.situation = Label(self.fenetre,textvariable=self.var,height=10)
		self.var.set("Bienvenue dans notre restaurant")
		self.panel.add(self.situation)

		self.commander=Button(self.fenetre, text="Commander", command=self.b_commande,height=10)
		self.panel.add(self.commander)
		self.num=num_client
        
		self.quitter=Button(self.fenetre,text="Quitter",command=self.b_quitter)
		self.panel.add(self.quitter)

		
	def b_commande(self):
		run_client(self.num,self)
	
	def b_quitter(self):
		sys.exit()

	def run (self) :
		self.fenetre.update_idletasks()
		self.fenetre.update()
		self.fenetre.mainloop()
	
	def chgt_situation(self,s):
		self.var.set(s)
		self.fenetre.update_idletasks()
		self.fenetre.update()









stopLoop = True

class client:
	
	def __init__(self,d,num):
		self.distance=d #Distance entre le client et le restaurant pour calculer le temps qu'il faudra pour qu'il soit livre
		self.num=num #Chaque client a un numero
	def commande(self):
		n=random.randint(0,10) #On pourrait faire par exemple 10 menus differents
		commande = "Menu "+str(n)
		return commande
		

if len(sys.argv)<2:
        print "Vous devez donner un numero au client"
        sys.exit(-1)		
        
num=sys.argv[1] #Il faut donner un numero au client au moment de sa connexion au serveur
client1=client(10,num)		
t=0
c=client1.commande()
I=Interface(num)
I.run()




