# setup_database.py
import sqlite3

def setup_database():
    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    # Creazione delle tabelle
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_classe TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS studenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cognome TEXT NOT NULL,
        classe_id INTEGER NOT NULL,
        FOREIGN KEY(classe_id) REFERENCES classi(id),
        UNIQUE(nome, cognome, classe_id)  -- Evita duplicati
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assenze (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        studente_id INTEGER NOT NULL,
        data DATE NOT NULL,
        quadrimestre INTEGER NOT NULL,
        FOREIGN KEY(studente_id) REFERENCES studenti(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        studente_id INTEGER NOT NULL,
        voto REAL NOT NULL,
        data DATE NOT NULL,
        quadrimestre INTEGER NOT NULL,
        FOREIGN KEY(studente_id) REFERENCES studenti(id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database configurato con successo!")

if __name__ == "__main__":
    setup_database()
