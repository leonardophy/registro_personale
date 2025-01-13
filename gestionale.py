#!/usr/bin/env python3

import sqlite3
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime
import os

# Configurazione del database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "registro.db")


# Funzione per selezionare il quadrimestre
def seleziona_quadrimestre():
    root = ttk.Window(themename="journal")
    root.title("Seleziona Quadrimestre")
    root.geometry("400x200")

    def seleziona_1_quadrimestre():
        root.withdraw()
        mostra_classi(1)

    def seleziona_2_quadrimestre():
        root.withdraw()
        mostra_classi(2)

    ttk.Label(root, text="Seleziona il Quadrimestre", font=("Arial", 16)).pack(pady=20)
    ttk.Button(root, text="1° Quadrimestre", bootstyle="success", command=seleziona_1_quadrimestre).pack(pady=10)
    ttk.Button(root, text="2° Quadrimestre", bootstyle="info", command=seleziona_2_quadrimestre).pack(pady=10)

    root.mainloop()


# Funzione per mostrare le classi
def mostra_classi(quadrimestre):
    classi_window = ttk.Window(themename="journal")
    classi_window.title("Seleziona Classe")
    classi_window.geometry("400x300")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_classe FROM classi")
    classi = cursor.fetchall()
    conn.close()

    ttk.Label(classi_window, text="Seleziona una Classe", font=("Arial", 16)).pack(pady=20)

    for classe_id, nome_classe in classi:
        ttk.Button(classi_window, text=nome_classe, bootstyle="success",
                   command=lambda classe_id=classe_id: mostra_studenti(classe_id, quadrimestre)).pack(pady=10)


# Funzione per mostrare la lista degli studenti
def mostra_studenti(classe_id, quadrimestre):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome_classe FROM classi WHERE id = ?", (classe_id,))
    nome_classe = cursor.fetchone()[0]
    conn.close()

    studenti_window = ttk.Window(themename="journal")
    studenti_window.title(f"Studenti - {nome_classe} - Quadrimestre {quadrimestre}")
    studenti_window.geometry("900x600")

    # Bottoni globali per la classe
    global_frame = ttk.Frame(studenti_window)
    global_frame.pack(fill=X, pady=10, padx=10)

    ttk.Button(global_frame, text="Visualizza Voti", bootstyle="primary",
               command=lambda: mostra_tabella_pivot(classe_id, quadrimestre)).pack(side=LEFT, padx=5)
    ttk.Button(global_frame, text="Aggiungi Lezione", bootstyle="success",
               command=lambda: gestisci_lezione(classe_id, nome_classe)).pack(side=LEFT, padx=5)
    ttk.Button(global_frame, text="Visualizza Lezioni", bootstyle="info",
               command=lambda: visualizza_lezioni(classe_id, nome_classe)).pack(side=LEFT, padx=5)
    ttk.Button(global_frame, text="Elimina Studente", bootstyle="danger",
           command=lambda: elimina_studente(classe_id)).pack(side=LEFT, padx=5)


    # Frame con scrollbar per la lista studenti
    scroll_frame = ttk.Frame(studenti_window)
    scroll_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    canvas = tk.Canvas(scroll_frame)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    content_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    # Recupera gli studenti dalla classe selezionata
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cognome FROM studenti WHERE classe_id = ?", (classe_id,))
    studenti = cursor.fetchall()
    conn.close()

    for studente_id, nome, cognome in studenti:
        student_frame = ttk.Frame(content_frame)
        student_frame.pack(fill=X, pady=5)

        ttk.Label(student_frame, text=f"{nome} {cognome}", width=30, anchor="w").pack(side=LEFT)

        ttk.Button(student_frame, text="Gestisci Voti", bootstyle="primary",
                   command=lambda studente_id=studente_id, nome=nome, cognome=cognome: gestione_voti(studente_id, nome, cognome, quadrimestre)).pack(side=LEFT, padx=5)

        ttk.Button(student_frame, text="Gestisci Assenze", bootstyle="warning",
                   command=lambda studente_id=studente_id, nome=nome, cognome=cognome: gestione_assenze(studente_id, nome, cognome, quadrimestre)).pack(side=LEFT, padx=5)


# Funzione per gestire le lezioni
def gestisci_lezione(classe_id, nome_classe):
    lezione_window = ttk.Window(themename="journal")
    lezione_window.title(f"Aggiungi Lezione - {nome_classe}")
    lezione_window.geometry("400x400")

    ttk.Label(lezione_window, text=f"Aggiungi Lezione - {nome_classe}", font=("Arial", 16)).pack(pady=10)

    ttk.Label(lezione_window, text="Argomento:").pack(pady=5)
    entry_argomento = ttk.Entry(lezione_window, width=50)
    entry_argomento.pack(pady=5)

    ttk.Label(lezione_window, text="Ore:").pack(pady=5)
    entry_ore = ttk.Entry(lezione_window, width=10)
    entry_ore.pack(pady=5)

    ttk.Label(lezione_window, text="Data (YYYY-MM-DD):").pack(pady=5)
    data_corrente = datetime.now().strftime("%Y-%m-%d")
    entry_data = ttk.Entry(lezione_window, width=20)
    entry_data.insert(0, data_corrente)
    entry_data.pack(pady=5)

    def salva_lezione():
        argomento = entry_argomento.get()
        ore = entry_ore.get()
        data = entry_data.get()

        if not argomento or not ore or not data:
            messagebox.showerror("Errore", "Tutti i campi sono obbligatori!")
            return

        try:
            ore = int(ore)
            datetime.strptime(data, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Errore", "Dati non validi!")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lezioni (classe_id, data, argomento, ore)
            VALUES (?, ?, ?, ?)
        """, (classe_id, data, argomento, ore))
        conn.commit()
        conn.close()

        messagebox.showinfo("Successo", "Lezione aggiunta con successo!")
        lezione_window.destroy()

    ttk.Button(lezione_window, text="Salva", bootstyle="success", command=salva_lezione).pack(pady=10)


# Funzione per visualizzare le lezioni
def visualizza_lezioni(classe_id, nome_classe):
    lezioni_window = ttk.Window(themename="journal")
    lezioni_window.title(f"Visualizza Lezioni - {nome_classe}")
    lezioni_window.geometry("800x500")

    ttk.Label(lezioni_window, text=f"Lezioni - {nome_classe}", font=("Arial", 16)).pack(pady=10)

    # Tabella per mostrare le lezioni
    lezioni_table = ttk.Treeview(lezioni_window, columns=("ID", "Data", "Argomento", "Ore"), show="headings", bootstyle="info")
    lezioni_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    lezioni_table.heading("ID", text="ID")
    lezioni_table.heading("Data", text="Data")
    lezioni_table.heading("Argomento", text="Argomento")
    lezioni_table.heading("Ore", text="Ore")
    lezioni_table.column("ID", anchor="center", width=50)
    lezioni_table.column("Data", anchor="center", width=150)
    lezioni_table.column("Argomento", anchor="w", width=400)
    lezioni_table.column("Ore", anchor="center", width=50)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, data, argomento, ore
        FROM lezioni
        WHERE classe_id = ?
        ORDER BY data DESC
    """, (classe_id,))
    lezioni = cursor.fetchall()
    conn.close()

    for lezione in lezioni:
        lezioni_table.insert("", "end", values=lezione)

    def modifica_lezione():
        selected_item = lezioni_table.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona una lezione da modificare.")
            return

        # Ottieni i dettagli della lezione selezionata
        lezione_id, data, argomento, ore = lezioni_table.item(selected_item)["values"]

        modifica_window = ttk.Window(themename="journal")
        modifica_window.title("Modifica Lezione")
        modifica_window.geometry("400x500")

        ttk.Label(modifica_window, text="Modifica Lezione", font=("Arial", 16)).pack(pady=10)

        ttk.Label(modifica_window, text="Data (YYYY-MM-DD):").pack(pady=5)
        entry_data = ttk.Entry(modifica_window, width=20)
        entry_data.insert(0, data)
        entry_data.pack(pady=5)

        ttk.Label(modifica_window, text="Argomento:").pack(pady=5)
        entry_argomento = ttk.Entry(modifica_window, width=50)
        entry_argomento.insert(0, argomento)
        entry_argomento.pack(pady=5)

        ttk.Label(modifica_window, text="Ore:").pack(pady=5)
        entry_ore = ttk.Entry(modifica_window, width=10)
        entry_ore.insert(0, ore)
        entry_ore.pack(pady=5)

        def salva_modifiche():
            nuova_data = entry_data.get()
            nuovo_argomento = entry_argomento.get()
            nuove_ore = entry_ore.get()

            if not nuova_data or not nuovo_argomento or not nuove_ore:
                messagebox.showerror("Errore", "Tutti i campi sono obbligatori!")
                return

            try:
                nuove_ore = int(nuove_ore)
                datetime.strptime(nuova_data, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Errore", "Formato dati non valido!")
                return

            # Aggiorna la lezione nel database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lezioni
                SET data = ?, argomento = ?, ore = ?
                WHERE id = ?
            """, (nuova_data, nuovo_argomento, nuove_ore, lezione_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Successo", "Lezione modificata con successo!")
            modifica_window.destroy()
            visualizza_lezioni(classe_id, nome_classe)

        ttk.Button(modifica_window, text="Salva Modifiche", bootstyle="success", command=salva_modifiche).pack(pady=10)

    def elimina_lezione():
        selected_item = lezioni_table.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona una lezione da eliminare.")
            return

        lezione_id = lezioni_table.item(selected_item)["values"][0]

        # Conferma eliminazione
        if messagebox.askyesno("Conferma Eliminazione", "Sei sicuro di voler eliminare questa lezione?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lezioni WHERE id = ?", (lezione_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Successo", "Lezione eliminata con successo!")
            visualizza_lezioni(classe_id, nome_classe)

    # Bottoni per modificare ed eliminare lezioni
    button_frame = ttk.Frame(lezioni_window)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Modifica Lezione", bootstyle="primary", command=modifica_lezione).pack(side=LEFT, padx=5)
    ttk.Button(button_frame, text="Elimina Lezione", bootstyle="danger", command=elimina_lezione).pack(side=LEFT, padx=5)



# Funzione per gestire i voti di uno studente
def gestione_voti(studente_id, nome, cognome, quadrimestre, parent_window=None):
    if parent_window:
        parent_window.destroy()  # Chiude la finestra precedente

    voti_window = ttk.Window(themename="journal")
    voti_window.title(f"Gestione Voti - {nome} {cognome}")
    voti_window.geometry("600x500")

    ttk.Label(voti_window, text=f"Voti di {nome} {cognome} - Quadrimestre {quadrimestre}", font=("Arial", 16)).pack(pady=10)

    # Tabella per mostrare i voti
    voti_table = ttk.Treeview(voti_window, columns=("ID", "Voto", "Data"), show="headings", bootstyle="info")
    voti_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    voti_table.heading("ID", text="ID")
    voti_table.heading("Voto", text="Voto")
    voti_table.heading("Data", text="Data")
    voti_table.column("ID", anchor="center", width=50)
    voti_table.column("Voto", anchor="center", width=100)
    voti_table.column("Data", anchor="center", width=150)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, voto, data
        FROM voti
        WHERE studente_id = ? AND quadrimestre = ?
        ORDER BY data DESC
    """, (studente_id, quadrimestre))
    voti = cursor.fetchall()
    conn.close()

    for voto in voti:
        voti_table.insert("", "end", values=voto)

    def aggiungi_voto():
        aggiungi_window = ttk.Window(themename="journal")
        aggiungi_window.title("Aggiungi Voto")
        aggiungi_window.geometry("400x200")

        ttk.Label(aggiungi_window, text="Voto:").pack(pady=5)
        entry_voto = ttk.Entry(aggiungi_window, width=10)
        entry_voto.pack(pady=5)

        ttk.Label(aggiungi_window, text="Data (YYYY-MM-DD):").pack(pady=5)
        entry_data = ttk.Entry(aggiungi_window, width=20)
        entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        entry_data.pack(pady=5)

        def salva_voto():
            voto = entry_voto.get()
            data = entry_data.get()

            if not voto or not data:
                messagebox.showerror("Errore", "Tutti i campi sono obbligatori!")
                return

            try:
                voto = float(voto)
                datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Errore", "Formato dati non valido!")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO voti (studente_id, voto, data, quadrimestre)
                VALUES (?, ?, ?, ?)
            """, (studente_id, voto, data, quadrimestre))
            conn.commit()
            conn.close()

            messagebox.showinfo("Successo", "Voto aggiunto con successo!")
            aggiungi_window.destroy()
            gestione_voti(studente_id, nome, cognome, quadrimestre, voti_window)

        ttk.Button(aggiungi_window, text="Salva", bootstyle="success", command=salva_voto).pack(pady=10)

    def modifica_voto():
        selected_item = voti_table.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona un voto da modificare.")
            return

        voto_id, voto_attuale, data_attuale = voti_table.item(selected_item)["values"]

        modifica_window = ttk.Window(themename="journal")
        modifica_window.title("Modifica Voto")
        modifica_window.geometry("400x300")

        ttk.Label(modifica_window, text="Modifica Voto", font=("Arial", 16)).pack(pady=10)

        ttk.Label(modifica_window, text="Voto:").pack(pady=5)
        entry_voto = ttk.Entry(modifica_window, width=20)
        entry_voto.insert(0, voto_attuale)
        entry_voto.pack(pady=5)

        ttk.Label(modifica_window, text="Data (YYYY-MM-DD):").pack(pady=5)
        entry_data = ttk.Entry(modifica_window, width=20)
        entry_data.insert(0, data_attuale)
        entry_data.pack(pady=5)

        def salva_modifiche():
            nuovo_voto = entry_voto.get()
            nuova_data = entry_data.get()

            if not nuovo_voto or not nuova_data:
                messagebox.showerror("Errore", "Tutti i campi sono obbligatori!")
                return

            try:
                nuovo_voto = float(nuovo_voto)
                datetime.strptime(nuova_data, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Errore", "Formato dati non valido!")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE voti
                SET voto = ?, data = ?
                WHERE id = ?
            """, (nuovo_voto, nuova_data, voto_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Successo", "Voto modificato con successo!")
            modifica_window.destroy()
            gestione_voti(studente_id, nome, cognome, quadrimestre, voti_window)

        ttk.Button(modifica_window, text="Salva Modifiche", bootstyle="success", command=salva_modifiche).pack(pady=10)

    def elimina_voto():
        selected_item = voti_table.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona un voto da eliminare.")
            return

        voto_id = voti_table.item(selected_item)["values"][0]

        if messagebox.askyesno("Conferma Eliminazione", "Sei sicuro di voler eliminare questo voto?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM voti WHERE id = ?", (voto_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Successo", "Voto eliminato con successo!")
            gestione_voti(studente_id, nome, cognome, quadrimestre, voti_window)

    button_frame = ttk.Frame(voti_window)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Aggiungi Voto", bootstyle="primary", command=aggiungi_voto).pack(side=LEFT, padx=5)
    ttk.Button(button_frame, text="Modifica Voto", bootstyle="info", command=modifica_voto).pack(side=LEFT, padx=5)
    ttk.Button(button_frame, text="Elimina Voto", bootstyle="danger", command=elimina_voto).pack(side=LEFT, padx=5)


# Funzione per gestire le assenze di uno studente
def gestione_assenze(studente_id, nome, cognome, quadrimestre):
    assenze_window = ttk.Window(themename="journal")
    assenze_window.title(f"Gestione Assenze - {nome} {cognome}")
    assenze_window.geometry("600x400")

    ttk.Label(assenze_window, text=f"Assenze di {nome} {cognome} - Quadrimestre {quadrimestre}", font=("Arial", 16)).pack(pady=10)

    assenze_table = ttk.Treeview(assenze_window, columns=("Data"), show="headings", bootstyle="warning")
    assenze_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    assenze_table.heading("Data", text="Data")
    assenze_table.column("Data", anchor="center", width=200)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data
        FROM assenze
        WHERE studente_id = ? AND quadrimestre = ?
        ORDER BY data DESC
    """, (studente_id, quadrimestre))
    assenze = cursor.fetchall()
    conn.close()

    for data in assenze:
        assenze_table.insert("", "end", values=(data[0],))

    def aggiungi_assenza():
        aggiungi_window = ttk.Window(themename="journal")
        aggiungi_window.title("Aggiungi Assenza")
        aggiungi_window.geometry("400x200")

        ttk.Label(aggiungi_window, text="Data (YYYY-MM-DD):").pack(pady=5)
        entry_data = ttk.Entry(aggiungi_window, width=20)
        entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        entry_data.pack(pady=5)

        def salva_assenza():
            data = entry_data.get()
            if not data:
                messagebox.showerror("Errore", "Inserisci una data!")
                return
            try:
                datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Errore", "Data non valida!")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO assenze (studente_id, data, quadrimestre)
                VALUES (?, ?, ?)
            """, (studente_id, data, quadrimestre))
            conn.commit()
            conn.close()

            messagebox.showinfo("Successo", "Assenza aggiunta con successo!")
            aggiungi_window.destroy()
            gestione_assenze(studente_id, nome, cognome, quadrimestre)

        ttk.Button(aggiungi_window, text="Salva", bootstyle="success", command=salva_assenza).pack(pady=10)

    ttk.Button(assenze_window, text="Aggiungi Assenza", bootstyle="primary", command=aggiungi_assenza).pack(pady=10)



# Funzione per mostrare la tabella pivot
def mostra_tabella_pivot(classe_id, quadrimestre):
    pivot_window = ttk.Window(themename="journal")
    pivot_window.title(f"Tabella Voti - Quadrimestre {quadrimestre}")
    pivot_window.geometry("1200x600")

    ttk.Label(pivot_window, text=f"Tabella Voti - Quadrimestre {quadrimestre}", font=("Arial", 16)).pack(pady=10)

    # Frame per organizzare le due tabelle
    tables_frame = ttk.Frame(pivot_window)
    tables_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Tabella per nomi e medie
    table_left = ttk.Treeview(tables_frame, show="headings", bootstyle="info", height=20)
    table_left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))

    # Tabella per voti
    table_right = ttk.Treeview(tables_frame, show="headings", bootstyle="info", height=20)
    table_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))

    # Configura la tabella di sinistra (nomi e medie)
    table_left["columns"] = ["Studente", "Media"]
    table_left.heading("Studente", text="Studente")
    table_left.heading("Media", text="Media")
    table_left.column("Studente", anchor="center", width=200)
    table_left.column("Media", anchor="center", width=100)

    # Configura la tabella di destra (voti per data)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ottieni le date dei voti
    cursor.execute("""
        SELECT DISTINCT substr(data, 6, 5) AS data
        FROM voti
        WHERE quadrimestre = ? AND studente_id IN (
            SELECT id FROM studenti WHERE classe_id = ?
        )
        ORDER BY data
    """, (quadrimestre, classe_id))
    date_columns = [row[0] for row in cursor.fetchall()]

    table_right["columns"] = date_columns
    for date in date_columns:
        table_right.heading(date, text=date)
        table_right.column(date, anchor="center", width=100)

    # Funzione per determinare il colore della media
    def get_color(value):
        if value >= 6:
            return "green"
        elif 5 <= value < 6:
            return "orange"
        else:
            return "red"

    # Popola le due tabelle
    cursor.execute("""
        SELECT studenti.id, studenti.nome || ' ' || studenti.cognome AS studente
        FROM studenti
        WHERE classe_id = ?
        ORDER BY studente
    """, (classe_id,))
    studenti = cursor.fetchall()

    for studente_id, studente in studenti:
        total_voti, count_voti = 0, 0
        row_voti = []

        for date in date_columns:
            cursor.execute("""
                SELECT voto
                FROM voti
                WHERE studente_id = ? AND substr(data, 6, 5) = ? AND quadrimestre = ?
            """, (studente_id, date, quadrimestre))
            voto = cursor.fetchone()
            if voto:
                voto = voto[0]
                total_voti += voto
                count_voti += 1
                row_voti.append(voto)
            else:
                row_voti.append("")

        # Calcola la media
        media = total_voti / count_voti if count_voti > 0 else 0
        media_value = f"{media:.2f}"

        # Inserisci nella tabella sinistra
        item_id = table_left.insert("", "end", values=(studente, media_value))

        # Applica colore alla media
        media_color = get_color(media)
        table_left.tag_configure(media_color, foreground=media_color, font=("Arial", 10, "bold"))
        table_left.item(item_id, tags=(media_color,))

        # Inserisci nella tabella destra
        table_right.insert("", "end", values=row_voti)

    conn.close()

def elimina_studente(classe_id):
    elimina_window = ttk.Window(themename="journal")
    elimina_window.title("Elimina Studente")
    elimina_window.geometry("600x400")

    ttk.Label(elimina_window, text="Seleziona uno studente da eliminare", font=("Arial", 16)).pack(pady=10)

    # Tabella per mostrare gli studenti
    studenti_table = ttk.Treeview(elimina_window, columns=("ID", "Nome", "Cognome"), show="headings", bootstyle="info")
    studenti_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    studenti_table.heading("ID", text="ID")
    studenti_table.heading("Nome", text="Nome")
    studenti_table.heading("Cognome", text="Cognome")
    studenti_table.column("ID", anchor="center", width=50)
    studenti_table.column("Nome", anchor="center", width=200)
    studenti_table.column("Cognome", anchor="center", width=200)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cognome FROM studenti WHERE classe_id = ?", (classe_id,))
    studenti = cursor.fetchall()
    conn.close()

    for studente in studenti:
        studenti_table.insert("", "end", values=studente)

    def conferma_eliminazione():
        selected_item = studenti_table.selection()
        if not selected_item:
            messagebox.showerror("Errore", "Seleziona uno studente da eliminare.")
            return

        studente_id, nome, cognome = studenti_table.item(selected_item)["values"]

        # Conferma eliminazione
        if messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare {nome} {cognome}?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM studenti WHERE id = ?", (studente_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Successo", f"Studente {nome} {cognome} eliminato con successo!")
            elimina_window.destroy()

    ttk.Button(elimina_window, text="Elimina Studente", bootstyle="danger", command=conferma_eliminazione).pack(pady=10)



# Avvio del gestionale
if __name__ == "__main__":
    seleziona_quadrimestre()
