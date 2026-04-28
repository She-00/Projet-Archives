import tkinter as tk
from tkinter import filedialog, messagebox

# ------------------------------
#   VARIABLES GLOBALES CHIP-8
# ------------------------------

rom = None  # contenu binaire de la ROM
memoire = [0] * 4096  # mémoire CHIP-8
ecran = [[0]*64 for _ in range(32)]  # écran 64x32

V = [0] * 16  # registres V0 à VF
I = 0  # registre d'adresse
pc = 0x200  # program counter (début des ROM)
stack = []
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

# ------------------------------
#   GESTION DU CLAVIER
# ------------------------------

def touche_appuyee(event):
    touche = event.char.lower()
    if touche in mapping_touch:
        clavier[mapping_touch[touche]] = 1
        print("Touche pressée :", mapping_touch[touche])

def touche_relachee(event):
    touche = event.char.lower()
    if touche in mapping_touch:
        clavier[mapping_touch[touche]] = 0

# ------------------------------
#   CHARGEMENT ROM
# ------------------------------

def charger_rom():
    global rom
    global pc
    pc = 0x200
    global memoire, ecran, V, I

    memoire = [0] * 4096
    ecran = [[0] * 64 for _ in range(32)]
    V = [0] * 16
    I = 0

    chemin = filedialog.askopenfilename(
        title="Sélectionner une ROM CHIP-8",
        filetypes=[("Fichier CHIP-8", "*.ch8")]
    )

    if not chemin:
        return

    try:
        with open(chemin, "rb") as f:
            rom = f.read()

            # chargement en mémoire à partir de 0x200
            for i, octet in enumerate(rom):
                memoire[0x200 + i] = octet

        print("ROM chargée :", chemin)
        print("Taille :", len(rom), "octets")

    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# ------------------------------
#   EXECUTION CPU
# ------------------------------

def executer_cycle():
    global pc, I

    if rom is None:
        return

    if pc >= 0x200 + len(rom):
        print("Fin de la ROM")
        return

    # FETCH
    opcode = (memoire[pc] << 8) | memoire[pc + 1]
    print("PC:", hex(pc), "Opcode:", hex(opcode))

    # DECODE + EXECUTE


    # 00E0 → clear screen
    if opcode == 0x00E0:
        print("Clear screen")
        for y in range(32):
            for x in range(64):
                ecran[y][x] = 0

    # 1NNN → jump
    elif opcode & 0xF000 == 0x1000:
        pc = opcode & 0x0FFF
        return

    # 6XKK → VX = KK
    elif opcode & 0xF000 == 0x6000:
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF
        V[x] = kk

    # 7XKK → VX += KK
    elif opcode & 0xF000 == 0x7000:
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF
        V[x] = (V[x] + kk) & 0xFF  # limite à 8 bits

    # ANNN → I = NNN
    elif opcode & 0xF000 == 0xA000:
        I = opcode & 0x0FFF

    # DXYN → dessiner sprite
    elif opcode & 0xF000 == 0xD000:

        x = V[(opcode & 0x0F00) >> 8]
        y = V[(opcode & 0x00F0) >> 4]
        n = opcode & 0x000F
        V[0xF] = 0

        for ligne in range(n):
            octet = memoire[I + ligne]

            for col in range(8):
                pixel = (octet >> (7 - col)) & 1

                if pixel == 1:
                    px = (x + col) % 64
                    py = (y + ligne) % 32

                    ecran[py][px] ^= 1

        dessiner_ecran()

    # 2NNN → CALL
    elif opcode & 0xF000 == 0x2000:
        stack.append(pc)
        pc = opcode & 0x0FFF
        return

    # 00EE → RETURN
    elif opcode == 0x00EE:
        pc = stack.pop()
        return

    # EX9E → touche pressée
    elif opcode & 0xF0FF == 0xE09E:
        x = (opcode & 0x0F00) >> 8
        if clavier[V[x]] == 1:
            pc += 2

    # EXA1 → touche NON pressée
    elif opcode & 0xF0FF == 0xE0A1:
        x = (opcode & 0x0F00) >> 8
        if clavier[V[x]] == 0:
            pc += 2

    elif opcode & 0xF000 == 0x3000:
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF

        if V[x] == kk:
            pc += 2

    elif opcode & 0xF000 == 0x4000:
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF

        if V[x] != kk:
            pc += 2

    elif opcode & 0xF000 == 0x8000:

        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F

        if n == 0x0:  # VX = VY
            V[x] = V[y]

        elif n == 0x1:  # OR
            V[x] |= V[y]

        elif n == 0x2:  # AND
            V[x] &= V[y]

        elif n == 0x3:  # XOR
            V[x] ^= V[y]

    elif opcode & 0xF0FF == 0xF029:
        x = (opcode & 0x0F00) >> 8
        I = V[x] * 5

    elif opcode & 0xF0FF == 0xF055:
        x = (opcode & 0x0F00) >> 8
        for i in range(x + 1):
            memoire[I + i] = V[i]

    elif opcode & 0xF0FF == 0xF065:
        x = (opcode & 0x0F00) >> 8
        for i in range(x + 1):
            V[i] = memoire[I + i]




    else:
        print("Opcode inconnu")

    pc += 2
    print("PC:", hex(pc))
    print("PC:", hex(pc), "Mémoire:", hex(memoire[pc]), hex(memoire[pc + 1]))

# ------------------------------
#   AFFICHAGE
# ------------------------------

def dessiner_ecran():
    canvas.delete("all")

    taille_pixel = 10

    for y in range(32):
        for x in range(64):
            if ecran[y][x] == 1:
                canvas.create_rectangle(
                    x * taille_pixel,
                    y * taille_pixel,
                    (x + 1) * taille_pixel,
                    (y + 1) * taille_pixel,
                    fill="white",
                    outline=""
                )

# ------------------------------
#   BOUCLE CPU
# ------------------------------

def boucle_cpu():
    executer_cycle()
    root.after(2, boucle_cpu)


# ------------------------------
#   INTERFACE
# ------------------------------


root = tk.Tk()
root.title("Emulateur CHIP-8 (début)")
root.geometry("660x370")

# gestion clavier
root.bind("<KeyPress>", touche_appuyee)
root.bind("<KeyRelease>", touche_relachee)

tk.Button(root, text="Charger ROM", command=charger_rom).pack(pady=10)
tk.Button(root, text="Lancer CPU", command=boucle_cpu).pack(pady=10)

canvas = tk.Canvas(root, width=640, height=320)
canvas.pack()


ecran[10][10] = 1
dessiner_ecran()

root.mainloop()