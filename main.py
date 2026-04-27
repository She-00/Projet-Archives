import tkinter as tk
from tkinter import filedialog, messagebox



# ------------------------------
#   FONCTIONS
# ------------------------------

rom_bytes = None  # stockage de la ROM chargée
memory = [0] * 4096
display = [[0]*64 for _ in range(32)]

# registres CHIP-8
V = [0] * 16
I = 0
pc = 0x200

def sel_rom():
    global rom_bytes
    path = filedialog.askopenfilename(
        title="Sélectionner une ROM CHIP-8",
        filetypes=[("Fichier CHIP-8", "*.ch8")]
    )

    if not path:
        return

    print(f"\n=== ROM sélectionnée ===\n{path}\n")

    try:
        with open(path, "rb") as f:
            rom_bytes = f.read()
            for i, b in enumerate(rom_bytes):
                memory[0x200 + i] = b

        print(f"Taille ROM : {len(rom_bytes)} octets")

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lire la ROM :\n{e}")


def show_sprite():
    if rom_bytes is None:
        messagebox.showerror("Erreur", "Aucune ROM chargée.")
        return

    try:
        addr = int(entry_addr.get(), 16)
    except:
        messagebox.showerror("Erreur", "Adresse invalide (utilise l’hex : 300, 2A0, etc.)")
        return

    # On récupère les lignes du sprite
    height = int(entry_height.get())
    sprite = memory[addr:addr + height]

    if len(sprite) < height:
        messagebox.showerror("Erreur", "Adresse hors ROM.")
        return

    draw_sprite(sprite)


def draw_sprite(sprite_data):
    win = tk.Toplevel()
    win.title("Aperçu Sprite CHIP-8")

    pixel_size = 64
    width = 32 * pixel_size
    height = len(sprite_data) * pixel_size

    canvas = tk.Canvas(win, width=width, height=height, bg="black")
    canvas.pack()

    for row_index, byte in enumerate(sprite_data): #BOUCLE FOR POUR COMPRENDRE LES SPRITS POUR LA MACHINE
        for bit_index in range(8):
            bit = (byte >> (7 - bit_index)) & 1
            if bit == 1:
                x = bit_index * pixel_size
                y = row_index * pixel_size
                canvas.create_rectangle(
                    x, y, x + pixel_size, y + pixel_size,
                    fill="white", outline=""
                )

def execute_cycle():
        global pc, I

        opcode = (memory[pc] << 8) | memory[pc + 1]

        print("Opcode:", hex(opcode))

        # 00E0 -> clear screen
        if opcode == 0x00E0:
            print("Clear screen")

        # 1NNN -> jump
        elif opcode & 0xF000 == 0x1000:
            addr = opcode & 0x0FFF
            pc = addr
            return

        # 6XKK -> VX = KK
        elif opcode & 0xF000 == 0x6000:

            x = (opcode & 0x0F00) >> 8
            kk = opcode & 0x00FF

            V[x] = kk
            print(f"V{x} = {kk}")

        # 7XKK -> VX += KK
        elif opcode & 0xF000 == 0x7000:
            x = (opcode & 0x0F00) >> 8
            kk = opcode & 0x00FF
            V[x] += kk
            print(f"V{x} += {kk}")

        # ANNN -> I = NNN
        elif opcode & 0xF000 == 0xA000:

            I = opcode & 0x0FFF
            print("I =", hex(I))

        elif opcode & 0xF000 == 0xD000:

            x = V[(opcode & 0x0F00) >> 8]
            y = V[(opcode & 0x00F0) >> 4]
            n = opcode & 0x000F

        print("Draw sprite")

        for row in range(n):

            sprite_byte = memory[I + row]

            for col in range(8):

                pixel = (sprite_byte >> (7 - col)) & 1

                if pixel == 1:
                    px = (x + col) % 64
                    py = (y + row) % 32

                    display[py][px] ^= 1
        else:
            print("Opcode inconnu")

        draw_display()
        pc += 2

def draw_display():
    win = tk.Toplevel()
    win.title("Ecran CHIP-8")

    pixel_size = 10

    canvas = tk.Canvas(win, width=64*pixel_size, height=32*pixel_size, bg="black")
    canvas.pack()

    for y in range(32):
        for x in range(64):

            if display[y][x] == 1:

                canvas.create_rectangle(
                    x*pixel_size,
                    y*pixel_size,
                    (x+1)*pixel_size,
                    (y+1)*pixel_size,
                    fill="white",
                    outline=""
                )

def cpu_loop():
    execute_cycle()

    # relance la boucle toutes les 200 ms
    root.after(200, cpu_loop)


# ------------------------------
#   INTERFACE GRAPHIQUE
# ------------------------------

root = tk.Tk() #ON IMPORTE LA CLASS TK
root.title("Lecteur de ROM CHIP-8 + Afficheur Sprite")
root.geometry("330x220") #taille de la fenetre
root.resizable(False, False)

btn_rom = tk.Button(root, text="Sélectionner une ROM .ch8", command=sel_rom) #bouton
btn_rom.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Adresse HEX du sprite :").grid(row=0, column=0)
entry_addr = tk.Entry(frame, width=8)
entry_addr.insert(0, "300")
entry_addr.grid(row=0, column=1)

tk.Label(frame, text="Hauteur (lignes) :").grid(row=1, column=0)
entry_height = tk.Entry(frame, width=8)
entry_height.insert(0, "5")
entry_height.grid(row=1, column=1)

btn_show = tk.Button(root, text="Afficher sprite", command=show_sprite)
btn_show.pack(pady=15)

btn_run = tk.Button(root, text="Lancer CPU", command=cpu_loop)
btn_run.pack(pady=10)

root.mainloop()
