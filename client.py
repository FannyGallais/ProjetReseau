import socket 
import select
import time
import sys
import signal
import random
from Tkinter import*



def run_client(num):
	print "je run"
	global stopLoop
	stopLoop=True
	try:

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(("",8001))
		
		while stopLoop:
			msg ="client"+str(num)+" en attente pour un "+c
			s.send(msg)
			data = s.recv(255)
			if data == "fin": stopLoop=False



	except socket.error, e:
			print "erreur dans l'appel a une methode de la classe socket: %s" % e
			sys.exit(1)
	finally:
		s.shutdown(1)
		s.close()
		print "Le client a recu sa commande"
		sys.exit()
		
	
	
	

class Interface:

	def __init__(self, num_client) :

		self.fenetre = Tk()
		self.fenetre.geometry("500x500")

		self.fenetre.title("COMMANDE")
		
		self.panel = PanedWindow(self.fenetre,orient=HORIZONTAL,height=750,width=1000)
		self.panel.pack()
		self.commander=Button(self.fenetre, text="Commander", command=self.b_commande, height=50)
		self.panel.add(self.commander)
		self.num=num_client
		self.quitter=Button(self.fenetre,text="Quitter",command=self.b_quitter,height=50)
		self.panel.add(self.quitter)
		
		
	def b_commande(self):
		run_client(self.num)
	
	def b_quitter(self):
		if stopLoop==True:
			print "Vous ne pouvez pas quitter car vous etes en cours de livraison"
		else:
			sys.exit(1)

	def run (self) :
		self.fenetre.update_idletasks()
		self.fenetre.update()
		self.fenetre.mainloop()







stopLoop = True

class client:
	
	def __init__(self,d,num):
		self.distance=d #Distance entre le client et le restaurant pour calculer le temps qu'il faudra pour qu'il soit livre
		self.num=num #Chaque client a un numero
	def commande(self):
		n=random.randint(0,10) #On pourrait faire par exemple 10 menus differents
		commande = "Menu"+str(n)
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



