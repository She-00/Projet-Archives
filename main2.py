# ------------------------------------
#   EMULATEUR CHIP-8 SIMPLE (BASE)
# ------------------------------------

# Mémoire CHIP-8 : 4096 octets
memoire = [0] * 4096

# Registres V0 à VF
V = [0] * 16

# Registre d'adresse I
I = 0

# Compteur ordinal (PC)
pc = 0x200   # Les programmes commencent à 0x200

# Écran 64x32 (0 = noir, 1 = blanc)
ecran = [[0]*64 for _ in range(32)]

# ------------------------------------
#   CHARGEMENT D’UNE ROM
# ------------------------------------

def charger_rom(chemin):
    global memoire

    with open(chemin, "rb") as f:
        rom = f.read()

    # On place la ROM en mémoire à partir de 0x200
    for i, octet in enumerate(rom):
        memoire[0x200 + i] = octet

    print("ROM chargée :", chemin)
    print("Taille :", len(rom), "octets")


# ------------------------------------
#   EXECUTION D’UN CYCLE CPU
# ------------------------------------

def cycle_cpu():
    global pc, I

    # On lit 2 octets = 1 instruction
    opcode = (memoire[pc] << 8) | memoire[pc + 1]
    print("PC =", hex(pc), "Opcode =", hex(opcode))

    # ------------------------------
    #   DECODAGE DES INSTRUCTIONS
    # ------------------------------

    # 00E0 : effacer l'écran
    if opcode == 0x00E0:
        for y in range(32):
            for x in range(64):
                ecran[y][x] = 0

    # 1NNN : saut à l'adresse NNN
    elif opcode & 0xF000 == 0x1000:
        adresse = opcode & 0x0FFF
        pc = adresse
        return

    # 6XKK : VX = KK
    elif opcode & 0xF000 == 0x6000:
        x = (opcode >> 8) & 0xF
        kk = opcode & 0xFF
        V[x] = kk

    # 7XKK : VX += KK
    elif opcode & 0xF000 == 0x7000:
        x = (opcode >> 8) & 0xF
        kk = opcode & 0xFF
        V[x] = (V[x] + kk) & 0xFF

    # ANNN : I = NNN
    elif opcode & 0xF000 == 0xA000:
        I = opcode & 0x0FFF

    else:
        print("Instruction non gérée :", hex(opcode))

    # On passe à l’instruction suivante
    pc += 2


# ------------------------------------
#   BOUCLE PRINCIPALE
# ------------------------------------

def executer(n_cycles):
    for _ in range(n_cycles):
        cycle_cpu()


# ------------------------------------
#   TEST
# ------------------------------------

charger_rom("PONG.ch8")
executer(20)
