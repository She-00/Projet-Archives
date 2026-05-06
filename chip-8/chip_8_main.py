

"""
pour push le code aller sur l'onglet en dessus des ficher (commit)
selectionner le ficher chip-8_main
et faite push and commit
pour voir si le push a fontionner sur le dernier onglet en bas a gauche (une sorte de branche avec des boulle)
regarder si le push est violet
vous pouvez mettre un commentaire quand vous pusher le main pour voir ce que vous avez mis en plus



voila
"""
import tkinter as tk
from tkinter import filedialog, messagebox

#Debut du code :
# code de naîma et nada : à mettre ici
# code de naima 
# memoire et structure de base chip-8
class Chip8:
    def __init__(self):

        # on cree 4096 cases de memoire
        self.memory = [0] * 4096

        # pour commencer le programme il faut 0x200
        self.pc = 0x200

        # on cree une pile de 16 emplacements
        self.stack = [0] * 16

        # la position de la pile
        self.sp = 0

    # ROM en mémoire
    def load_rom(self, filename):

        # on ouvre le fichier ROM en mode binaire
        with open(filename, "rb") as file:
            rom = file.read()

        # on copie la ROM dans la memoire
        for i in range(len(rom)):
            self.memory[0x200 + i] = rom[i]
      
# TEST
chip8 = Chip8()
print("Mémoire :", len(chip8.memory))
print("PC :", chip8.pc)
print("SP :", chip8.sp)
print("Pile :", len(chip8.stack))      


# ------------------------------
#   VARIABLES GLOBALES CHIP-8
# ------------------------------
"""
fhgfjks
"""
k=4
h=5
u=4
# ------------------------------
#   GESTION DU CLAVIER / TIMER SOUND
# ------------------------------


# clavier CHIP-8 (16 touches)
clavier = [0] * 16

# mapping clavier PC → CHIP-8
mapping_touch = {
    '1': 0x1, '2': 0x2, '3': 0x3, '4': 0xC,
    'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
    'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
    'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF
}
#timer son
delay_timer = 0
sound_timer = 0

def touche_appuyee(event):
    touche = event.char.lower()
    if touche in mapping_touch:
        clavier[mapping_touch[touche]] = 1
        print("Touche pressée :", mapping_touch[touche])

def touche_relachee(event):
    touche = event.char.lower()
    if touche in mapping_touch:
        clavier[mapping_touch[touche]] = 0
        print("Touche relachee :", mapping_touch[touche])



# ------------------------------
#   CHARGEMENT ROM
# ------------------------------




# ------------------------------
#   BOUCLE CPU
# ------------------------------







# ------------------------------
#   INTERFACE
# ------------------------------









# gestion clavier
#root.bind("<KeyPress>", touche_appuyee)
#root.bind("<KeyRelease>", touche_relachee)