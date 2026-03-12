# La torre di Hanoi

Implementazione con interfaccia grafica in Python (Tkinter) del gioco della Torre di Hanoi, con salvataggio risultati su SQLite e classifica Top 10 per numero di dischi.

## Stato attuale

- GUI funzionante in `hanoi-gui.py`.
- Salvataggio risultati su database locale `hanoi.sqlite`.
- Classifiche separate per numero di dischi (`risultati_<n>`).

## GUI (Python) - hanoi-gui.py

Avvio:

```bash
python3 hanoi-gui.py
```

Requisiti:
- Python 3.x
- Tkinter (di solito incluso; su alcune distro Linux può richiedere pacchetto separato)

Troubleshooting:
- Se vedi `ModuleNotFoundError: No module named 'tkinter'`, installa il pacchetto Tkinter della tua distribuzione (es. `python3-tk` su Debian/Ubuntu).
- macOS: Tkinter è incluso con l’installer ufficiale di Python; se manca, reinstalla Python dal sito ufficiale.
- Windows: Tkinter è incluso con l’installer ufficiale di Python; se manca, ripara o reinstalla Python.

Uso:
- `Dischi`: imposta il numero di dischi (1-10).
- `Giocatore`: nome usato per salvare i risultati.
- `Start Auto`: risolve automaticamente la torre.
- `Reset`: azzera la partita.
- `Top 10`: mostra la classifica per il numero di dischi indicato in `Dischi`.
- `Velocità`: regola la velocità dell’auto-solver.
- Modalità manuale: clicca il palo di origine e poi quello di destinazione.

Persistenza:
- I risultati vengono salvati su SQLite in `hanoi.sqlite`.
- Esiste una tabella per ogni numerosità di dischi (`risultati_3`, `risultati_4`, ...).
- La Top 10 prioritizza chi ha usato il numero minimo di mosse e poi il tempo più basso.

## File principali

- `hanoi-gui.py`: GUI del gioco.
- `hanoi-gui.pl`: versione GUI in Perl (se presente).
- `hanoi.pl`: versione testuale in Perl (se presente).
