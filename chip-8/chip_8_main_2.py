import pygame
import sys

# =========================================================
#                         CHIP-8
# =========================================================

# Sprites des chiffres 0-F (polices intégrées du CHIP-8)
# Ces 80 octets doivent être chargés en mémoire au démarrage (adresses 0x000 à 0x04F)
# Chaque chiffre fait 5 octets (5 lignes de 8 pixels)
FONTSET = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80,  # F
]


# code de naima
class Chip8:
    def __init__(self):
        # 4096 cases de mémoire
        self.memory = [0] * 4096

        # Le programme commence à l'adresse 0x200
        self.pc = 0x200

        # Pile de 16 emplacements (pour les appels de sous-routines)
        self.stack = [0] * 16

        # Pointeur de pile
        self.sp = 0

        # 16 registres V0 à VF
        self.V = [0] * 16

        # Timers
        self.delay_timer = 0
        self.sound_timer = 0

        # Clavier (16 touches)
        self.keys = [0] * 16

        # Registre d'adresse I
        self.I = 0

        # CORRECTION : chargement des fontsets en mémoire
        # Les sprites des chiffres sont placés au début de la mémoire (0x000)
        for i in range(len(FONTSET)):
            self.memory[i] = FONTSET[i]

    # -----------------------------------------------------
    # CHARGEMENT ROM
    # -----------------------------------------------------

    def load_rom(self, filename):
        # On ouvre le fichier ROM en mode binaire
        with open(filename, "rb") as file:
            rom = file.read()

        # On copie la ROM dans la mémoire à partir de 0x200
        for i in range(len(rom)):
            self.memory[0x200 + i] = rom[i]

    # -----------------------------------------------------
    # FETCH : lire l'opcode en mémoire
    # -----------------------------------------------------

    def fetch(self):
        # Un opcode fait 2 octets : on combine memory[pc] et memory[pc+1]
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2
        return opcode

    # -----------------------------------------------------
    # DECODE ET EXECUTE
    # -----------------------------------------------------

    def decode_and_execute(self, opcode):
        # On délègue tout à execute_opcode (plus besoin de doublon)
        self.execute_opcode(opcode)

    # -----------------------------------------------------
    # EXECUTION OPCODES
    # -----------------------------------------------------

    def execute_opcode(self, opcode):
        x   = (opcode & 0x0F00) >> 8   # numéro du registre X
        y   = (opcode & 0x00F0) >> 4   # numéro du registre Y
        nn  = opcode & 0x00FF           # constante sur 8 bits
        nnn = opcode & 0x0FFF           # adresse sur 12 bits
        n   = opcode & 0x000F           # constante sur 4 bits

        # 00E0 — Effacer l'écran
        if opcode == 0x00E0:
            clear_screen()

        # CORRECTION : 00EE — Retour de sous-routine
        elif opcode == 0x00EE:
            self.sp -= 1
            self.pc = self.stack[self.sp]

        # 1NNN — Saut à l'adresse NNN
        elif (opcode & 0xF000) == 0x1000:
            self.pc = nnn

        # CORRECTION : 2NNN — Appel de sous-routine à NNN
        elif (opcode & 0xF000) == 0x2000:
            self.stack[self.sp] = self.pc   # on sauvegarde l'adresse de retour
            self.sp += 1
            self.pc = nnn

        # CORRECTION : 3XNN — Sauter si V[x] == nn
        elif (opcode & 0xF000) == 0x3000:
            if self.V[x] == nn:
                self.pc += 2

        # CORRECTION : 4XNN — Sauter si V[x] != nn
        elif (opcode & 0xF000) == 0x4000:
            if self.V[x] != nn:
                self.pc += 2

        # CORRECTION : 5XY0 — Sauter si V[x] == V[y]
        elif (opcode & 0xF000) == 0x5000:
            if self.V[x] == self.V[y]:
                self.pc += 2

        # 6XNN — Mettre nn dans V[x]
        elif (opcode & 0xF000) == 0x6000:
            self.V[x] = nn

        # 7XNN — Ajouter nn à V[x]
        elif (opcode & 0xF000) == 0x7000:
            self.V[x] = (self.V[x] + nn) & 0xFF

        # 8XYN — Opérations sur les registres
        elif (opcode & 0xF000) == 0x8000:
            self.op_8XYN(x, y, n)

        # CORRECTION : 9XY0 — Sauter si V[x] != V[y]
        elif (opcode & 0xF000) == 0x9000:
            if self.V[x] != self.V[y]:
                self.pc += 2

        # ANNN — Mettre NNN dans I
        elif (opcode & 0xF000) == 0xA000:
            self.I = nnn

        # CORRECTION : BNNN — Sauter à NNN + V[0]
        elif (opcode & 0xF000) == 0xB000:
            self.pc = nnn + self.V[0]

        # CORRECTION : CXNN — V[x] = nombre aléatoire AND nn
        elif (opcode & 0xF000) == 0xC000:
            import random
            self.V[x] = random.randint(0, 255) & nn

        # DXYN — Dessiner un sprite
        elif (opcode & 0xF000) == 0xD000:
            draw_sprite(self, x, y, n)

        # EX9E — Sauter si la touche V[x] est pressée
        elif (opcode & 0xF0FF) == 0xE09E:
            if self.keys[self.V[x]]:
                self.pc += 2

        # EXA1 — Sauter si la touche V[x] n'est PAS pressée
        elif (opcode & 0xF0FF) == 0xE0A1:
            if not self.keys[self.V[x]]:
                self.pc += 2

        # FX07 — V[x] = delay_timer
        elif (opcode & 0xF0FF) == 0xF007:
            self.V[x] = self.delay_timer

        # FX0A — Attendre une touche et la mettre dans V[x]
        elif (opcode & 0xF0FF) == 0xF00A:
            for i in range(16):
                if self.keys[i]:
                    self.V[x] = i
                    return
            self.pc -= 2  # recommencer l'instruction si aucune touche

        # FX15 — delay_timer = V[x]
        elif (opcode & 0xF0FF) == 0xF015:
            self.delay_timer = self.V[x]

        # FX18 — sound_timer = V[x]
        elif (opcode & 0xF0FF) == 0xF018:
            self.sound_timer = self.V[x]

        # CORRECTION : FX1E — I = I + V[x]
        elif (opcode & 0xF0FF) == 0xF01E:
            self.I = (self.I + self.V[x]) & 0xFFFF

        # CORRECTION : FX29 — I pointe vers le sprite du chiffre V[x]
        # Chaque sprite fait 5 octets, ils commencent à l'adresse 0x000
        elif (opcode & 0xF0FF) == 0xF029:
            self.I = self.V[x] * 5

        # CORRECTION : FX33 — Stocker V[x] en BCD (centaines, dizaines, unités)
        elif (opcode & 0xF0FF) == 0xF033:
            self.memory[self.I]     = self.V[x] // 100
            self.memory[self.I + 1] = (self.V[x] // 10) % 10
            self.memory[self.I + 2] = self.V[x] % 10

        # CORRECTION : FX55 — Sauvegarder V[0]..V[x] en mémoire à partir de I
        elif (opcode & 0xF0FF) == 0xF055:
            for i in range(x + 1):
                self.memory[self.I + i] = self.V[i]

        # CORRECTION : FX65 — Charger V[0]..V[x] depuis la mémoire à partir de I
        elif (opcode & 0xF0FF) == 0xF065:
            for i in range(x + 1):
                self.V[i] = self.memory[self.I + i]

        else:
            print("Opcode inconnu :", hex(opcode))

    # -----------------------------------------------------
    # OPCODES 8XYN — opérations sur registres
    # -----------------------------------------------------

    def op_8XYN(self, x, y, n):
        # 8XY0 — V[x] = V[y]
        if n == 0x0:
            self.V[x] = self.V[y]

        # CORRECTION : 8XY1 — V[x] = V[x] OR V[y]  (c'était AND avant, c'est faux)
        elif n == 0x1:
            self.V[x] = self.V[x] | self.V[y]

        # CORRECTION : 8XY2 — V[x] = V[x] AND V[y]  (c'était XOR avant, c'est faux)
        elif n == 0x2:
            self.V[x] = self.V[x] & self.V[y]

        # CORRECTION : 8XY3 — V[x] = V[x] XOR V[y]  (c'était une addition avant, c'est faux)
        elif n == 0x3:
            self.V[x] = self.V[x] ^ self.V[y]

        # 8XY4 — V[x] = V[x] + V[y], VF = retenue
        elif n == 0x4:
            result = self.V[x] + self.V[y]
            self.V[0xF] = 1 if result > 255 else 0
            self.V[x] = result & 0xFF

        # 8XY5 — V[x] = V[x] - V[y], VF = 1 si pas d'emprunt
        elif n == 0x5:
            self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0
            self.V[x] = (self.V[x] - self.V[y]) & 0xFF

        # 8XY6 — V[x] décalage droit, VF = bit perdu
        elif n == 0x6:
            self.V[0xF] = self.V[x] & 0x1
            self.V[x] = self.V[x] >> 1

        # CORRECTION : 8XY7 — V[x] = V[y] - V[x], VF = 1 si pas d'emprunt
        elif n == 0x7:
            self.V[0xF] = 1 if self.V[y] >= self.V[x] else 0
            self.V[x] = (self.V[y] - self.V[x]) & 0xFF

        # 8XYE — V[x] décalage gauche, VF = bit perdu
        elif n == 0xE:
            self.V[0xF] = (self.V[x] >> 7) & 0x1
            self.V[x] = (self.V[x] << 1) & 0xFF

        else:
            print("Sous-opcode 8XY" + hex(n) + " inconnu")


# =========================================================
#                   VARIABLES GLOBALES
# =========================================================

SCALE     = 10
WIDTH     = 64
HEIGHT    = 32
COLOR_ON  = (255, 255, 255)
COLOR_OFF = (0, 0, 0)

# Grille de pixels : False = éteint, True = allumé
screen = [[False] * WIDTH for _ in range(HEIGHT)]

# Mapping clavier CHIP-8 → touches du clavier
# Clavier CHIP-8 :  1 2 3 C      Touches PC : 1 2 3 4
#                   4 5 6 D                    Q W E R
#                   7 8 9 E                    A S D F
#                   A 0 B F                    Z X C V
mapping_touch = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
}


# =========================================================
#                   INITIALISATION
# =========================================================

chip8 = Chip8()

pygame.init()
pygame.display.set_caption("CHIP-8 - Les Archives du Futur")
window = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
clock = pygame.time.Clock()

# Charger la ROM
chip8.load_rom("test_opcode.ch8")


# =========================================================
#                     AFFICHAGE
# =========================================================

# Code Bélinda

def draw_screen(window):
    """Redessine toute la fenêtre à partir de la grille screen."""
    window.fill(COLOR_OFF)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if screen[y][x]:
                pygame.draw.rect(window, COLOR_ON,
                                 (x * SCALE, y * SCALE, SCALE, SCALE))
    pygame.display.flip()


def clear_screen():
    """Instruction 00E0 — Efface tous les pixels."""
    for y in range(HEIGHT):
        for x in range(WIDTH):
            screen[y][x] = False


def draw_sprite(chip, x_reg, y_reg, n):
    """
    Instruction DXYN — Dessine un sprite de n lignes.
    Le sprite est en mémoire à partir de l'adresse chip.I.
    Les pixels sont en XOR : allumé devient éteint et inversement.
    chip.V[0xF] est mis à 1 s'il y a une collision (pixel éteint par XOR).
    """
    x_start = chip.V[x_reg] % WIDTH
    y_start = chip.V[y_reg] % HEIGHT
    chip.V[0xF] = 0  # reset collision

    for row in range(n):
        sprite_byte = chip.memory[chip.I + row]
        for col in range(8):
            if sprite_byte & (0x80 >> col):
                x = (x_start + col) % WIDTH
                y = (y_start + row) % HEIGHT
                if screen[y][x]:
                    chip.V[0xF] = 1   # collision détectée
                screen[y][x] ^= True  # XOR


# =========================================================
#                      TIMERS
# =========================================================

def update_timers():
    """Décrémente les timers à chaque frame (60 Hz)."""
    if chip8.delay_timer > 0:
        chip8.delay_timer -= 1

    if chip8.sound_timer > 0:
        chip8.sound_timer -= 1
        print("BEEP")  # ici on pourrait jouer un vrai son


# =========================================================
#                  BOUCLE CPU
# =========================================================

def executer_cycle():
    """Lit, décode et exécute un opcode."""
    opcode = chip8.fetch()
    # CORRECTION : on appelle bien decode_and_execute (et non execute_opcode directement)
    chip8.decode_and_execute(opcode)


# =========================================================
#                  BOUCLE PRINCIPALE
# =========================================================

running = True

while running:

    # Gestion des événements
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in mapping_touch:
                key = mapping_touch[event.key]
                chip8.keys[key] = 1   # CORRECTION : on utilise uniquement chip8.keys
                print("Touche pressée :", hex(key))

        elif event.type == pygame.KEYUP:
            if event.key in mapping_touch:
                key = mapping_touch[event.key]
                chip8.keys[key] = 0   # CORRECTION : on utilise uniquement chip8.keys
                print("Touche relâchée :", hex(key))

    # Exécuter un cycle CPU
    executer_cycle()

    # Mettre à jour les timers
    update_timers()

    # Afficher l'écran
    draw_screen(window)

    # 60 fps
    clock.tick(60)

pygame.quit()
