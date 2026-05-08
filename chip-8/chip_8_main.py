

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


# ------------------------------
#   VARIABLES GLOBALES CHIP-8
# ------------------------------
"""
fhgfjks
"""
k=4
h=5
u=4
j=5
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
def executer_cycle():
    global pc, I, stack
    if pc >= 0x200 + len(rom):
        print("Fin de la ROM")
        return

    # FETCH
    opcode = (memoire[pc] << 8) | memoire[pc + 1]
    print("PC:", hex(pc), "Opcode:", hex(opcode))

    # Extraction des champs
    x = (opcode >> 8) & 0xF
    y = (opcode >> 4) & 0xF
    n = opcode & 0xF
    kk = opcode & 0xFF
    nnn = opcode & 0x0FFF

    # SAUTS, APPELS, COMPARAISONS person4
    
    if (opcode & 0xF000) == 0x1000:          
        pc = nnn
        return
    elif (opcode & 0xF000) == 0x2000:        
        stack.append(pc)
        pc = nnn
        return
    elif opcode == 0x00EE:                  
        pc = stack.pop()
        return
    elif (opcode & 0xF000) == 0x3000:        
        if V[x] == kk:
            pc += 2
    elif (opcode & 0xF000) == 0x4000:        
        if V[x] != kk:
            pc += 2
    elif (opcode & 0xF00F) == 0x5000:        
        if V[x] == V[y]:
            pc += 2
    elif (opcode & 0xF00F) == 0x9000:        
        if V[x] != V[y]:
            pc += 2
    elif (opcode & 0xF000) == 0xB000:       
        pc = nnn + V[0]
        return






# ------------------------------
#   INTERFACE
# ------------------------------









# gestion clavier
#root.bind("<KeyPress>", touche_appuyee)
#root.bind("<KeyRelease>", touche_relachee)