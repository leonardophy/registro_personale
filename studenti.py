# studenti.py

import sqlite3

def inserisci_studenti():
    # Connessione al database SQLite
    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    # Inserire classi solo se non esistono
    # Sostituire 'Classe A' e 'Classe B' con i nomi effettivi delle classi se necessario
    cursor.execute("INSERT OR IGNORE INTO classi (nome_classe) VALUES ('Classe A')")
    cursor.execute("INSERT OR IGNORE INTO classi (nome_classe) VALUES ('Classe B')")
    conn.commit()

    # Recuperare gli ID delle classi
    cursor.execute("SELECT id FROM classi WHERE nome_classe = 'Classe A'")
    classe_a_id = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM classi WHERE nome_classe = 'Classe B'")
    classe_b_id = cursor.fetchone()[0]

    # Inserire gli studenti per ogni classe, evitando duplicati
    # Sostituire i nomi e cognomi con dei placeholder generici
    studenti_classe_a = [
        ("Studente1", "Cognome1"),
        ("Studente2", "Cognome2"),
        ("Studente3", "Cognome3"),
        ("Studente4", "Cognome4"),
        ("Studente5", "Cognome5")
    ]
    studenti_classe_b = [
        ("Studente6", "Cognome6"),
        ("Studente7", "Cognome7"),
        ("Studente8", "Cognome8"),
        ("Studente9", "Cognome9"),
        ("Studente10", "Cognome10")
    ]

    for nome, cognome in studenti_classe_a:
        cursor.execute(
            """
            INSERT OR IGNORE INTO studenti (nome, cognome, classe_id) VALUES (?, ?, ?)
            """, (nome, cognome, classe_a_id))

    for nome, cognome in studenti_classe_b:
        cursor.execute(
            """
            INSERT OR IGNORE INTO studenti (nome, cognome, classe_id) VALUES (?, ?, ?)
            """, (nome, cognome, classe_b_id))

    conn.commit()
    conn.close()
    print("Classi e studenti inseriti con successo!")

if __name__ == "__main__":
    inserisci_studenti()
