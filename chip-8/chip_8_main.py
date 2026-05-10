

"""
pour push le code aller sur l'onglet en dessus des ficher (commit)
selectionner le ficher chip-8_main
et faite push and commit
pour voir si le push a fontionner sur le dernier onglet en bas a gauche (une sorte de branche avec des boulle)
regarder si le push est violet
vous pouvez mettre un commentaire quand vous pusher le main pour voir ce que vous avez mis en plus



voila
"""
import pygame

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

        self.V = [0] * 16
        self.delay_timer = 0
        self.sound_timer = 0
        self.keys = [0] * 16

    # ROM en mémoire
    def load_rom(self, filename):

        # on ouvre le fichier ROM en mode binaire
        with open(filename, "rb") as file:
            rom = file.read()

        # on copie la ROM dans la memoire
        for i in range(len(rom)):
            self.memory[0x200 + i] = rom[i]


    def execute_opcode(self,opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        nn = opcode & 0x00FF

        if (opcode & 0xF000) == 0x6000:
            self.op_6XNN(x, nn)

        elif (opcode & 0xF000) == 0x7000:
            self.op_7XNN(x, nn)

        elif (opcode & 0xF000) == 0x8000:
            n = opcode & 0x000F
            self.op_8XYN(x, y, n)

        elif (opcode & 0xF0FF) == 0xE09E:
            self.op_EX9E(x)

        elif (opcode & 0xF0FF) == 0xE0A1:
            self.op_EXA1(x)

        elif (opcode & 0xF0FF) == 0xF007:
            self.op_FX07(x)

        elif (opcode & 0xF0FF) == 0xF015:
            self.op_FX15(x)

        elif (opcode & 0xF0FF) == 0xF018:
            self.op_FX18(x)

        elif (opcode & 0xF0FF) == 0xF00A:
            self.op_FX0A(x)

        else:
            print("Opcode inconnu :",hex(opcode))


    def op_6XNN(self, x, nn):
        self.V[x] = nn

    def op_7XNN(self, x, nn):
        self.V[x] = (self.V[x] + nn) & 0xFF


    def op_8XYN(self, x, y, n):
        if n == 0x0:
            self.V[x] = self.V[y]

        elif n == 0x1:
            self.V[x] = self.V[x] & self.V[y]

        elif n == 0x2:
            self.V[x] = self.V[x] ^ self.V[y]

        elif n == 0x3:
            resultat = self.V[x] + self.V[y]
            self.V[0xF] = 1 if resultat > 0xFF else 0
            self.V[x] = resultat & 0xFF

        elif n == 0x4:
            self.V[0xF] = 1 if self.V[x] > self.V[y] else 0
            self.V[x] = (self.V[x] - self.V[y]) & 0xFF

        elif n == 0x5:
            self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
            self.V[x] = (self.V[y] - self.V[x]) & 0xFF

        elif n == 0x6:
            self.V[0xF] = self.V[x] & 0x1
            self.V[x] = self.V[x] >> 1

        elif n == 0xE:
            self.V[0xF] = (self.V[x] >> 7) & 0x1
            self.V[x] = (self.V[x] << 1) & 0xFF

        else:
            print("Sous-opcode 8XY",hex(n),"inconnu")

    def op_EX9E(self, x):
        if self.keys[self.V[x]]:
            self.pc += 2

    def op_EXA1(self, x):
        if not self.keys[self.V[x]]:
            self.pc += 2

    def op_FX07(self, x):
        self.V[x] = self.delay_timer

    def op_FX15(self, x):
        self.delay_timer = self.V[x]

    def op_FX18(self, x):
        self.sound_timer = self.V[x]

    def op_FX0A(self, x):
        for i in range(16):
            if self.keys[i]:
                self.V[x] = i
                return

        self.pc -= 2
      

# TEST
chip8 = Chip8()
print("Mémoire :", len(chip8.memory))
print("PC :", chip8.pc)
print("SP :", chip8.sp)
print("Pile :", len(chip8.stack))
print("TEST 6XNN : SET")
chip8.execute_opcode(0x6A42)
print("V[10] =",chip8.V[10],"(attendu : 66)")

# Code NADA : ajout de I, fetch, decode 
def _patch_chip8():
    # Ajouter I dans __init__
    original_init = Chip8.__init__
    def new_init(self):
        original_init(self)
        self.I = 0
    Chip8.__init__ = new_init

    # Ajouter fetch
    def fetch(self):
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2
        return opcode
    Chip8.fetch = fetch

    # Ajouter decode et execute
    def decode_and_execute(self, opcode):
        high = (opcode & 0xF000) >> 12
        if high == 0xA:
            self.I = opcode & 0x0FFF
        elif high == 0x6:
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.V[x] = nn
        else:
            self.execute_opcode(opcode)
    Chip8.decode_and_execute = decode_and_execute

    # Ajouter cycle
    def cycle(self):
        opcode = self.fetch()
        self.decode_and_execute(opcode)
    Chip8.cycle = cycle

_patch_chip8()
# fin 
# ------------------------------
#   VARIABLES GLOBALES CHIP-8
# ------------------------------

k=4
h=5
u=4
j=5
# ------------------------------
#   GESTION DU CLAVIER / TIMER SOUND
# ------------------------------

#clavier
clavier = [0]* 16
# mapping clavier PC → CHIP-8
""""
mapping_touch = {
    '1': 0x1, '2': 0x2, '3': 0x3, '4': 0xC,
    'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
    'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
    'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF
}


mapping_touch = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xC,

    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xD,

    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xE,

    pygame.K_z: 0xA,
    pygame.K_x: 0x0,
    pygame.K_c: 0xB,
    pygame.K_v: 0xF
}
"""

def touche_appuyee(event):
    touche = event.char.lower()
    if touche in mapping_touch:
        clavier[mapping_touch[touche]] = 1
        chip8.keys[mapping_touch[touche]] = 1
        print("Touche pressée :", mapping_touch[touche])

def touche_relachee(event):
    touche = event.char.lower()
    if touche in mapping_touch:
        clavier[mapping_touch[touche]] = 0
        chip8.keys[mapping_touch[touche]] = 0
        print("Touche relachee :", mapping_touch[touche])

def update_timers():
    if chip8.delay_timer > 0:
        chip8.delay_timer -= 1

    if chip8.sound_timer > 0:
        chip8.sound_timer -= 1
        print("BEEP")




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