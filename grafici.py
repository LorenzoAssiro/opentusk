import matplotlib
matplotlib.use('Agg')  # Usa backend non interattivo per evitare problemi con i thread
from flask import Flask, render_template_string
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

anno = 2019

# Funzione per leggere e analizzare i dati della popolazione per fasce d'età
def analizza_popolazione(file_path, anno):
    df = pd.read_csv(file_path, sep=',', quotechar='"')

    # Filtra le righe non numeriche (es. Totale o Non specificata)
    df = df[df['Età'].str.isnumeric()]  

    # Converte l'età in intero
    df['Età'] = df['Età'].astype(int)

    # Verifica se l'anno selezionato è presente tra le colonne
    if str(anno) not in df.columns:
        raise ValueError(f"Dati non disponibili per l'anno {anno}")
    
    # Raggruppa per fascia d'età e somma il campo dell'anno selezionato
    df['Fascia età'] = pd.cut(df['Età'], bins=range(0, 106, 15), right=False, include_lowest=True)
    df['Fascia età'] = df['Fascia età'].apply(lambda x: f"{int(x.left)} - {int(x.right - 1)}")
    
    popolazione_per_fascia = df.groupby('Fascia età')[str(anno)].sum().reset_index()
    
    # Calcola la percentuale per ogni fascia d'età
    popolazione_per_fascia['Percentuale'] = (popolazione_per_fascia[str(anno)] / popolazione_per_fascia[str(anno)].sum()) * 100

    return popolazione_per_fascia


# Funzione per analizzare le cause di morte per ogni territorio
def analizza_cause_morte_per_territorio(file_path):
    df = pd.read_csv(file_path, sep=',', quotechar='"')

    # Filtra i dati del 2021
    df = df[df['TIME'] == 2021]

    # Rimuovi le righe che contengono la parola 'Totale' nella colonna 'Causa iniziale di morte - European Short List'
    df = df[~df['Causa iniziale di morte - European Short List'].str.contains('Totale', case=False, na=False)]

    # Raggruppa per territorio e causa di morte
    territori = df['Territorio'].unique()
    cause_per_territorio = {
        territorio: df[df['Territorio'] == territorio]
        .groupby('Causa iniziale di morte - European Short List')['Value'].sum().reset_index()
        for territorio in territori
    }

    return cause_per_territorio

# Funzione per creare grafici a torta e convertirli in base64 per HTML (Per la popolazione)
def crea_grafico_torta(dati, labels, titolo, soglia_percentuale=5):
    # Filtra i settori con percentuali basse
    dati_filtrati = [d for d in dati if d >= soglia_percentuale]
    labels_filtrati = [labels[i] for i in range(len(dati)) if dati[i] >= soglia_percentuale]
    
    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(dati_filtrati, labels=labels_filtrati, autopct='%1.1f%%', startangle=140, 
                                       labeldistance=1.2, pctdistance=0.85, textprops={'fontsize': 10})

    # Impostare il titolo
    plt.title(titolo)
    plt.tight_layout()

    # Aggiungere margini per evitare sovrapposizioni
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    # Salvataggio in buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    return grafico_base64

# Funzione per creare grafici a colonne e convertirli in base64 per HTML (Per la mortalità)
def crea_grafico_colonne(dati, labels, titolo, soglia_percentuale=5):
    # Filtra i settori con percentuali basse
    dati_filtrati = [d for d in dati if d >= soglia_percentuale]
    labels_filtrati = [labels[i] for i in range(len(dati)) if dati[i] >= soglia_percentuale]
    
    plt.figure(figsize=(10, 6))
    
    # Crea il grafico a colonne
    plt.bar(labels_filtrati, dati_filtrati, color='skyblue')

    # Impostare il titolo e le etichette
    plt.title(titolo)
    plt.xlabel('Causa di morte')
    plt.ylabel('Valore')

    # Rotazione etichette per evitare sovrapposizioni
    plt.xticks(rotation=45, ha='right')

    # Salvataggio in buffer
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    return grafico_base64

# File CSV di input
file_popolazione = {
    'Bari': r'C:\\Users\\loren\\OneDrive\\Desktop\\Programmazione\\python\\Hackaton\\BARI.csv',
    'Lecce': r'C:\\Users\\loren\\OneDrive\\Desktop\\Programmazione\\python\\Hackaton\\LECCE.csv',
    'Foggia': r'C:\\Users\\loren\\OneDrive\\Desktop\\Programmazione\\python\\Hackaton\\FOGGIA.csv',
    'Brindisi': r'C:\\Users\\loren\\OneDrive\\Desktop\\Programmazione\\python\\Hackaton\\BRINDISI.csv',
    'Taranto' : r'C:\\Users\\loren\\OneDrive\\Desktop\\Programmazione\\python\\Hackaton\\TARANTO.csv',
    'B-A-T' : r'C:\\Users\\loren\\OneDrive\\Desktop\\Programmazione\\python\\Hackaton\\BAT.csv'
}

file_cause_morte = r'C:\\Users\\loren\\OneDrive\\Desktop\\Programmazione\\python\\Hackaton\\MORTI.csv'

# Creazione dell'app Flask
app = Flask(__name__)

@app.route('/')
def home():
    grafici_html = ""

    # Grafici a torta per la popolazione per fasce d'età
    for provincia, file_path in file_popolazione.items():
        df_popolazione = analizza_popolazione(file_path, anno)

        labels = df_popolazione['Fascia età']
        dati = df_popolazione['Percentuale']
        grafico_base64 = crea_grafico_torta(dati, labels, f'Percentuale Popolazione per Fascia d\'Età - {provincia}')

        grafici_html += f'<h3>Percentuale della Popolazione per Fascia d\'Età - {provincia}</h3>'
        grafici_html += f'<img src="data:image/png;base64,{grafico_base64}" alt="Grafico {provincia}">'

    # Grafici a colonne per cause di morte per ogni territorio
    cause_per_territorio = analizza_cause_morte_per_territorio(file_cause_morte)

    for territorio, df_cause in cause_per_territorio.items():
        if not df_cause.empty:
            labels = df_cause['Causa iniziale di morte - European Short List']
            dati = df_cause['Value']
            grafico_cause_base64 = crea_grafico_colonne(dati, labels, f'Cause di Morte - {territorio} (2021)')

            grafici_html += f'<h3>Cause di Morte - {territorio} (2021)</h3>'
            grafici_html += f'<img src="data:image/png;base64,{grafico_cause_base64}" alt="Grafico Cause di Morte {territorio}">'
        else:
            grafici_html += f'<h3>Cause di Morte - {territorio} (2021)</h3>'
            grafici_html += '<p>Nessun dato disponibile per questo territorio.</p>'

    # Template HTML
    template = f'''
    <html>
        <head>
            <title>Analisi Popolazione e Cause di Morte</title>
        </head>
        <body>
            <h1>Analisi della Popolazione e delle Cause di Morte</h1>
            {grafici_html}
        </body>
    </html>
    '''
    return render_template_string(template)

if __name__ == '__main__':
    app.run(debug=True)
