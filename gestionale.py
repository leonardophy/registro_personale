#!/usr/bin/env python3

import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import tkinter as tk
from datetime import datetime
import os

# Determina il percorso del file eseguibile o dello script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "registro.db")


# Funzione per selezionare il quadrimestre
def seleziona_quadrimestre():
    root = tk.Tk()
    root.title("Seleziona Quadrimestre")
    root.geometry("300x200")

    def seleziona_1_quadrimestre():
        root.withdraw()
        mostra_classi(1)

    def seleziona_2_quadrimestre():
        root.withdraw()
        mostra_classi(2)

    ttk.Label(root, text="Seleziona il Quadrimestre", font=("Arial", 12)).pack(pady=20)
    ttk.Button(root, text="1° Quadrimestre", command=seleziona_1_quadrimestre, bootstyle="success").pack(pady=10)
    ttk.Button(root, text="2° Quadrimestre", command=seleziona_2_quadrimestre, bootstyle="info").pack(pady=10)

    root.mainloop()


# Funzione per mostrare le classi
def mostra_classi(quadrimestre):
    classi_window = tk.Toplevel()
    classi_window.title("Seleziona la classe")
    classi_window.geometry("300x300")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_classe FROM classi")
    classi = cursor.fetchall()
    conn.close()

    for classe_id, nome_classe in classi:
        ttk.Button(classi_window, text=nome_classe, command=lambda classe_id=classe_id: mostra_studenti(classe_id, quadrimestre), bootstyle="success").pack(pady=10)


# Funzione per mostrare gli studenti di una classe
def mostra_studenti(classe_id, quadrimestre):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Recupera il nome della classe
    cursor.execute("SELECT nome_classe FROM classi WHERE id = ?", (classe_id,))
    nome_classe = cursor.fetchone()[0]


    studenti_window = tk.Toplevel()
    studenti_window.title(f"Gestione Studenti {nome_classe} - Quadrimestre {quadrimestre}")
    studenti_window.geometry("800x370+25+25")

    frame_studenti = ttk.Frame(studenti_window)
    frame_studenti.pack(fill=BOTH, expand=True, padx=10, pady=10)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome, cognome FROM studenti WHERE classe_id = ?", (classe_id,))
    studenti = cursor.fetchall()

    if not studenti:
        ttk.Label(frame_studenti, text="Nessuno studente trovato in questa classe.", font=("Arial", 14)).pack(pady=20)
        return

    for studente in studenti:
        studente_id = studente[0]
        nome = studente[1]
        cognome = studente[2]

        student_frame = ttk.Frame(frame_studenti)
        student_frame.pack(fill=X, pady=5)

        ttk.Label(student_frame, text=f"{nome} {cognome}", width=30, anchor="w").pack(side=LEFT)

        voti_button = ttk.Button(student_frame, text="Gestisci Voti", bootstyle="info",
                                 command=lambda studente_id=studente_id, nome=nome, cognome=cognome: gestione_voti(studente_id, nome, cognome, quadrimestre))
        voti_button.pack(side=LEFT, padx=5)

        assenze_button = ttk.Button(student_frame, text="Gestisci Assenze", bootstyle="warning",
                                    command=lambda studente_id=studente_id, nome=nome, cognome=cognome: gestione_assenze(studente_id, nome, cognome, quadrimestre))
        assenze_button.pack(side=LEFT, padx=5)

    conn.close()

    # Apre la finestra con la tabella pivot
    mostra_tabella_pivot(classe_id, quadrimestre)


# Funzione per mostrare la tabella pivot
def mostra_tabella_pivot(classe_id, quadrimestre):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Recupera il nome della classe
    cursor.execute("SELECT nome_classe FROM classi WHERE id = ?", (classe_id,))
    nome_classe = cursor.fetchone()[0]

    pivot_window = tk.Toplevel()
    pivot_window.title(f"Voti {nome_classe} - Quadrimestre {quadrimestre}")
    pivot_window.geometry("1200x300+25+500")

    ttk.Label(pivot_window, text=f"Voti Classe {nome_classe} (Quadrimestre {quadrimestre})", font=("Arial", 16)).pack(pady=10)

    frame = ttk.Frame(pivot_window)
    frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Configura lo stile
    style = ttk.Style()
    style.configure("Treeview", rowheight=30)
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

    # Treeview per il nome e la media
    name_media_table = ttk.Treeview(frame, show="headings", bootstyle="info", height=20)
    name_media_table.pack(side=LEFT, fill=Y)

    # Treeview per i voti
    voti_table = ttk.Treeview(frame, show="headings", bootstyle="info", height=20)
    voti_table.pack(side=LEFT, fill=BOTH, expand=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Recupera le date uniche (formattate come MM-GG)
    cursor.execute("""
        SELECT DISTINCT substr(data, 6, 5) AS data
        FROM voti
        WHERE quadrimestre = ? AND studente_id IN (
            SELECT id FROM studenti WHERE classe_id = ?
        )
        ORDER BY data
    """, (quadrimestre, classe_id))
    date = [row[0] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT id, nome || ' ' || cognome AS studente
        FROM studenti
        WHERE classe_id = ?
        ORDER BY studente
    """, (classe_id,))
    studenti = cursor.fetchall()

    # Definizione delle colonne
    name_media_columns = ["Studente", "Media"]
    voti_columns = date

    name_media_table["columns"] = name_media_columns
    voti_table["columns"] = voti_columns

    for col in name_media_columns:
        name_media_table.heading(col, text=col)
        name_media_table.column(col, anchor="center", width=150)

    for col in voti_columns:
        voti_table.heading(col, text=col)
        voti_table.column(col, anchor="center", width=100)

    # Alternanza dei colori delle righe
    name_media_table.tag_configure("oddrow", background="#f2f2f2")
    name_media_table.tag_configure("evenrow", background="#ffffff")
    name_media_table.tag_configure("media_verde", font=("Arial", 12, "bold"), foreground="green")
    name_media_table.tag_configure("media_gialla", font=("Arial", 12, "bold"), foreground="orange")
    name_media_table.tag_configure("media_rossa", font=("Arial", 12, "bold"), foreground="red")

    voti_table.tag_configure("oddrow", background="#f2f2f2")
    voti_table.tag_configure("evenrow", background="#ffffff")

    # Popolamento della tabella
    for index, (studente_id, studente) in enumerate(studenti):
        total_voti = 0
        count_voti = 0
        voti_row = []

        for data in date:
            cursor.execute("""
                SELECT voto
                FROM voti
                WHERE studente_id = ? AND substr(data, 6, 5) = ? AND quadrimestre = ?
            """, (studente_id, data, quadrimestre))
            voto = cursor.fetchone()
            if voto:
                total_voti += voto[0]
                count_voti += 1
                voti_row.append(voto[0])
            else:
                voti_row.append("")

        # Calcola la media
        media = total_voti / count_voti if count_voti > 0 else 0
        media_str = f"{media:.2f}"

        # Determina il colore della media
        if media >= 6:
            media_tag = "media_verde"
        elif media >= 5:
            media_tag = "media_gialla"
        else:
            media_tag = "media_rossa"

        # Alternanza delle righe
        row_tag = "evenrow" if index % 2 == 0 else "oddrow"

        # Inserisci il nome e la media nella prima tabella
        name_media_table.insert("", "end", values=(studente, media_str), tags=(row_tag, media_tag))

        # Inserisci i voti nella seconda tabella
        voti_table.insert("", "end", values=voti_row, tags=(row_tag,))

    conn.close()





# Funzione per gestire i voti
def gestione_voti(studente_id, nome, cognome, quadrimestre):
    voti_window = tk.Toplevel()
    voti_window.title(f"Voti di {nome} {cognome} - Quadrimestre {quadrimestre}")
    voti_window.geometry("800x800")

    ttk.Label(voti_window, text=f"Voti di {nome} {cognome}", font=("Arial", 16)).pack(pady=10)

    voti_table = ttk.Treeview(voti_window, columns=("ID", "Voto", "Data"), show="headings", bootstyle="info")
    voti_table.heading("ID", text="ID")
    voti_table.heading("Voto", text="Voto")
    voti_table.heading("Data", text="Data")
    voti_table.column("ID", width=50, anchor="center")
    voti_table.column("Voto", width=100, anchor="center")
    voti_table.column("Data", width=200, anchor="center")
    voti_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, voto, data FROM voti WHERE studente_id = ? AND quadrimestre = ?", (studente_id, quadrimestre))
    voti = cursor.fetchall()

    for voto_id, voto, data in voti:
        voti_table.insert("", "end", values=(voto_id, voto, data))

    def modifica_voto():
        selected_item = voti_table.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona un voto da modificare!")
            return

        item = voti_table.item(selected_item[0])
        voto_id, voto_corrente, data_corrente = item["values"]

        modifica_window = tk.Toplevel()
        modifica_window.title("Modifica Voto")
        modifica_window.geometry("400x300")

        ttk.Label(modifica_window, text="Voto Corrente").pack(pady=5)
        ttk.Entry(modifica_window, state="readonly", textvariable=tk.StringVar(value=voto_corrente)).pack()

        ttk.Label(modifica_window, text="Nuovo Voto").pack(pady=5)
        entry_nuovo_voto = ttk.Entry(modifica_window)
        entry_nuovo_voto.pack()

        ttk.Label(modifica_window, text="Data Corrente").pack(pady=5)
        ttk.Entry(modifica_window, state="readonly", textvariable=tk.StringVar(value=data_corrente)).pack()

        ttk.Label(modifica_window, text="Nuova Data (YYYY-MM-DD)").pack(pady=5)
        entry_nuova_data = ttk.Entry(modifica_window)
        entry_nuova_data.pack()

        def salva_modifica():
            nuovo_voto = entry_nuovo_voto.get()
            nuova_data = entry_nuova_data.get()

            if not nuovo_voto or not nuova_data:
                messagebox.showerror("Errore", "Inserisci un nuovo voto e una nuova data!")
                return

            try:
                nuovo_voto = float(nuovo_voto)
                datetime.strptime(nuova_data, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Errore", "Dati non validi!")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE voti SET voto = ?, data = ? WHERE id = ?",
                (nuovo_voto, nuova_data, voto_id)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Successo", "Voto modificato con successo!")
            modifica_window.destroy()
            gestione_voti(studente_id, nome, cognome, quadrimestre)

        ttk.Button(modifica_window, text="Salva Modifica", command=salva_modifica, bootstyle="success").pack(pady=10)

    def elimina_voto():
        selected_item = voti_table.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona un voto da eliminare!")
            return

        item = voti_table.item(selected_item[0])
        voto_id = item["values"][0]

        risposta = messagebox.askyesno("Conferma Eliminazione", "Sei sicuro di voler eliminare questo voto?")
        if risposta:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM voti WHERE id = ?", (voto_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Successo", "Voto eliminato con successo!")
            gestione_voti(studente_id, nome, cognome, quadrimestre)

    ttk.Button(voti_window, text="Modifica Voto", command=modifica_voto, bootstyle="primary").pack(pady=10)
    ttk.Button(voti_window, text="Elimina Voto", command=elimina_voto, bootstyle="danger").pack(pady=10)

    conn.close()

# Funzione per gestire le assenze
def gestione_assenze(studente_id, nome, cognome, quadrimestre):
    assenze_window = tk.Toplevel()
    assenze_window.title(f"Assenze di {nome} {cognome} - Quadrimestre {quadrimestre}")
    assenze_window.geometry("600x400")

    ttk.Label(assenze_window, text=f"Assenze di {nome} {cognome}", font=("Arial", 16)).pack(pady=10)

    assenze_table = ttk.Treeview(assenze_window, columns=("Data"), show="headings", bootstyle="warning")
    assenze_table.heading("Data", text="Data")
    assenze_table.column("Data", width=200, anchor="center")
    assenze_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM assenze WHERE studente_id = ? AND quadrimestre = ?", (studente_id, quadrimestre))
    assenze = cursor.fetchall()
    conn.close()

    for data in assenze:
        assenze_table.insert("", "end", values=(data[0],))

    def inserisci_assenza():
        inserimento_window = tk.Toplevel()
        inserimento_window.title("Inserisci Assenza")
        inserimento_window.geometry("400x200")

        ttk.Label(inserimento_window, text="Data (YYYY-MM-DD)").pack(pady=5)
        entry_data = ttk.Entry(inserimento_window)
        entry_data.pack()

        def salva_assenza():
            data = entry_data.get()

            if not data:
                messagebox.showerror("Errore", "Inserisci una data!")
                return

            try:
                datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Errore", "Inserisci una data valida!")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO assenze (studente_id, data, quadrimestre) VALUES (?, ?, ?)", 
                           (studente_id, data, quadrimestre))
            conn.commit()
            conn.close()
            messagebox.showinfo("Successo", "Assenza inserita con successo!")
            inserimento_window.destroy()
            gestione_assenze(studente_id, nome, cognome, quadrimestre)

        ttk.Button(inserimento_window, text="Salva", command=salva_assenza, bootstyle="success").pack(pady=10)

    ttk.Button(assenze_window, text="Inserisci Nuova Assenza", command=inserisci_assenza, bootstyle="primary").pack(pady=10)


# Avvio del gestionale
if __name__ == "__main__":
    seleziona_quadrimestre()
