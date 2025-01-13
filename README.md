# Gestionale per Studenti e Classi

Questo progetto è un gestionale semplice per monitorare i voti e le assenze di studenti in diverse classi, suddivisi per quadrimestri. Il software è scritto in **Python** e utilizza **Tkinter** per l'interfaccia grafica, **SQLite** per la gestione del database e **ttkbootstrap** per uno stile moderno delle finestre.

Tutto il progetto è stato creato con il supporto di ChatGPT.

---

## **Funzionalità**

- **Selezione del quadrimestre**: Puoi gestire i voti e le assenze separatamente per il primo o il secondo quadrimestre.
- **Gestione delle classi**: Visualizza gli studenti per ogni classe.
- **Gestione degli studenti**:
  - Inserisci, visualizza e modifica i voti.
  - Inserisci e visualizza le assenze.
- **Tabella pivot**:
  - Visualizza i voti in un formato tabellare con i giorni come intestazioni di colonna.
  - Mostra la media dei voti accanto al nome dello studente, con colori dinamici basati sul valore.

---

## **Requisiti**

Per eseguire questo progetto, hai bisogno di:
- **Python 3.9+**
- Librerie Python:
  - `ttkbootstrap`
  - `sqlite3` (inclusa in Python)
  - `tkinter` (inclusa in Python su molte piattaforme)

---

## **Installazione**

1. **Clona il repository:**
   ```bash
   git clone https://github.com/leonardophy/registro_personale.git
   cd registro_personale
   ```

2. **Installa le dipendenze richieste:**
   ```bash
   pip install ttkbootstrap
   ```

3. **Configura il database:**
   Esegui lo script per creare le tabelle nel database:
   ```bash
   python setup_database.py
   ```

4. **Aggiungi classi e studenti:**
   Esegui lo script per popolare il database con dati iniziali:
   ```bash
   python studenti.py
   ```

5. **Avvia il gestionale:**
   Esegui il file principale per utilizzare l'applicazione:
   ```bash
   python gestionale.py
   ```

---

## **Come Usare**

### **1. Seleziona un quadrimestre**
Quando avvii il gestionale, ti verrà richiesto di scegliere un quadrimestre (1° o 2°). Questa selezione determinerà i dati che stai visualizzando o modificando.

### **2. Scegli una classe**
Verrà visualizzata una lista di classi. Seleziona la classe che vuoi gestire.

### **3. Gestione degli studenti**
Per ogni studente, puoi:
- **Gestire i voti**: Aggiungere, visualizzare, modificare o eliminare voti.
- **Gestire le assenze**: Inserire e visualizzare le date delle assenze.

### **4. Visualizza la tabella pivot**
La tabella pivot mostra i voti di tutti gli studenti di una classe, con una colonna separata per ogni data. La media dei voti viene mostrata accanto al nome dello studente, colorata in base al valore:
- **Verde**: Media >= 6
- **Giallo**: 5 <= Media < 6
- **Rosso**: Media < 5

---

## **File Principali**

- **`setup_database.py`**: Configura il database SQLite con le tabelle necessarie.
- **`studenti.py`**: Inserisce classi e studenti come dati iniziali.
- **`gestionale.py`**: Il file principale che esegue l'applicazione.

---

## **Personalizzazioni**
Puoi adattare il progetto:
- Aggiungendo nuove classi e studenti modificando lo script `studenti.py`.
- Modificando il layout o le funzionalità direttamente in `gestionale.py`.

---

## **Contributi**
Se hai suggerimenti o vuoi contribuire, sentiti libero di inviare una **pull request** o aprire un **issue** nel repository.

---

## **Licenza**
Questo progetto è distribuito sotto la licenza MIT. Per maggiori dettagli, consulta il file [LICENSE](LICENSE).
