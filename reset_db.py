import sqlite3

def reset_database():
    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    # Elimina tutti i dati
    cursor.execute("DELETE FROM studenti;")
    cursor.execute("DELETE FROM classi;")

    conn.commit()
    conn.close()
    print("Database resettato con successo!")

if __name__ == "__main__":
    reset_database()
