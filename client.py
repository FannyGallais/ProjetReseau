import socket 
import select
import time
import sys
import signal
import random
import time
from Tkinter import*


#Cette fonction est centrale, elle permet la connexion du client au serveur
def run_client(client,I):
	client.commande=I.liste.get(I.liste.curselection()) #Le client choisit sa commande
	I.chgt_situation("Traitement de la commande en cours\n En attente d'un livreur disponible")
	global stopLoop
	stopLoop=True
	try:

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(("",8001))
		t=0
		while stopLoop:
			
			msg ="client"+str(client.num)+" en attente pour un "+client.commande
			s.send(msg)
			data = s.recv(255)
			if t==0:
				print data[1:]
				I.chgt_situation("Traitement de la commande en cours\n le livreur "+data[0]+" s'occupe de la livraison") #Pour savoir par quel livreur est pris en charge le client
			t+=1
			
			if data == "fin": 
				print data
				I.chgt_situation("Votre commande a bien ete livree\n Vous pouvez commander de nouveau ou quitter")
				stopLoop=False
				
			if data == "fin_attente": 
				print data
				I.chgt_situation("Votre commande a bien ete livree, nous nous excusons pour l'attente!\n Vous pouvez commander de nouveau ou quitter")
				stopLoop=False
				
			if data[0:5] == "Temps":
				print data
				I.v.set(data)
				
			if data=="bloque":
				I.chgt_situation("Vous ne pouvez plus passer de commande, le restaurant est ferme.\n Veuillez cliquer sur Quitter")
				I.bloque=True
				s.close()

	except socket.error, e:
			I.chgt_situation("Vous ne pouvez plus passer de commande, le restaurant est ferme.\n Veuillez cliquer sur quitter")
			
	finally:

		s.close()

		
	
	
#########################################################################################
#								PARTIE INTERFACE DU CLIENT								#
#########################################################################################	

class Interface:

	def __init__(self, client) :

		self.fenetre = Tk()
		self.fenetre.geometry("500x500")

		self.fenetre.title("CLIENT "+str(client.num))

		self.panel = PanedWindow(self.fenetre,orient=VERTICAL,height=750,width=1000)
		self.panel.pack()
		self.var = StringVar()
		self.situation = Label(self.fenetre,textvariable=self.var,height=5)
		self.var.set("Bienvenue dans notre restaurant\n Selectionnez le menu que vous voulez puis cliquez sur Commander")
		self.panel.add(self.situation)
		
		self.liste = Listbox(self.fenetre)
		self.liste.insert(1, "Menu1(10euros)")
		self.liste.insert(2, "Menu2(12euros)")
		self.liste.insert(3, "Menu3(13euros)")
		self.liste.insert(4, "Menu4(15euros)")
		self.liste.insert(5, "Menu5(6euros)")
		self.liste.insert(6, "Menu6(9euros)")
		self.liste.insert(7, "Menu7(11 euros)")
		self.liste.insert(8, "Menu8(10euros)")
		self.liste.insert(9, "Menu9(9euros)")
		self.liste.insert(10, "Menu10(8euros)")
		self.panel.add(self.liste)
		
		self.commander=Button(self.fenetre, text="Commander", command=self.b_commande,height=7)
		self.panel.add(self.commander)
        
		self.quitter=Button(self.fenetre,text="Quitter",command=self.b_quitter,height=5)
		self.panel.add(self.quitter)
		self.client=client
		
		self.v=StringVar()
		self.attente = Label(self.fenetre, textvariable=self.v, bg="white")
		self.v.set("Temps d'attente")
		self.attente.pack()
		self.panel.add(self.attente)
		
		self.bloque= False
		
	def b_commande(self):
		
		#On commence par verifier que le client a selectionne un menu
		Menu_select=False
		for i in xrange(self.liste.size()):
			if self.liste.selection_includes(i)==1: Menu_select=True
			
		if self.bloque ==False and Menu_select==True:
			run_client(self.client,self)
		
		#Si le client est bloque, cela veut dire que le restaurant est ferme	
		elif self.bloque==True :
			self.chgt_situation("Vous ne pouvez plus passer de commande, le restaurant est ferme.\n Veuillez cliquer sur quitter")
			
		elif Menu_select==False:
			self.chgt_situation("Vous devez selectionner un menu avant de cliquer sur Commander!")
			
	
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







#############################################################################
#								PARTIE CLIENT								#
#############################################################################

stopLoop = True

class client:
	
	def __init__(self,num):
		self.num=num #Chaque client a un numero
		self.commande=""

#Il faut donner un numero au client au moment de l'execution
if len(sys.argv)<2:
        print "Vous devez donner un numero au client"
        sys.exit(-1)		
        
num=sys.argv[1] 
client1=client(num)		
t=0
I=Interface(client1)

I.run()




