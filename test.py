import pandas as pd

# Funzione per visualizzare le voci uniche della colonna 'Causa iniziale di morte - European Short List'
def visualizza_voci_uniche(file_path):
    # Carica il dataset
    df = pd.read_csv(file_path, sep=',', quotechar='"')

    # Estrai le voci uniche dalla colonna 'Causa iniziale di morte - European Short List'
    voci_uniche = df['Causa iniziale di morte - European Short List'].unique()

    # Stampa le voci uniche
    print("Voci uniche nella colonna 'Causa iniziale di morte - European Short List':")
    for voce in voci_uniche:
        print(voce)

# Percorso del file CSV delle cause di morte
file_cause_morte = r'C:\\Users\\loren\\OneDrive\\Desktop\\Programmazione\\python\\Hackaton\\Cause di morte.csv'

# Visualizza le voci uniche
visualizza_voci_uniche(file_cause_morte)
