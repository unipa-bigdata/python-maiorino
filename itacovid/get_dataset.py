import os
import pandas as pd
from .check_csv_extension import check_csv_extension

def my_kaggle_api(username, key):
    """
        Funzione opzionale: da utilizzare in alternativa alla procedura ufficiale descritta su www.kaggle.com
        Inserire sottoforma di stringa l'username e la key di Kaggle.
        Esempio:
            my_kaggle_api('my_username', 'my_key')
    """
    os.environ['KAGGLE_username'] = str(username)
    os.environ['KAGGLE_key'] = str(key)

def download_covid_dataset(path=None, name=None):
    """
        Inserire sottoforma di stringa l'eventuale percorso di download e il nome che si vuole assegnare al file
        (includere l'estensione .csv è opzionale).
        Entrambi i valori sono opzionali.
        Se non si inserisce un percorso, di default il file scaricato viene memorizzato con il nome originale
        nella cartella in cui si sta lavorando.
        Esempio in ambiente UNIX:
            download_covid_dataset(path='/Users/user_name/Desktop', name='covid_dataset.csv')
        Esempio in ambiente WINDOWS:
            download_covid_dataset(path='C:/Users/user_name/Desktop', name='covid_dataset.csv')
            download_covid_dataset(path='C:\\Users\\User_name\\Desktop', name='covid_dataset.csv')
    """
    from kaggle.api.kaggle_api_extended import KaggleApi
    #Ho inserito qui l'import delle API di Kaggle perchè voglio che vengano importate solo se si tenta un download.
    #Se il file su cui si vuole lavorare è già in nostro possesso basta richiamare solamente la funzione: read_covid_dataset
    #Inoltre se effettuassi l'import prima di definire le variabili d'ambiente con l'username e key di Kaggle mi darebbe un errore

    api = KaggleApi()
    api.authenticate()

    #api.dataset_download_file(dataset='sudalairajkumar/covid19-in-italy', file_name='covid19_italy_region.csv', path=path, force=True)
    #non so perchè ma a volte con questa funzione il file scaricato ha un nome diverso
    api.dataset_download_files(dataset='sudalairajkumar/covid19-in-italy', path=path, force=True, unzip=True)
    #non potendo usare la funzione per scaricare il singolo file, rimuovo i file in più scaricati
    if path is None:
        path = os.getcwd()
    os.remove(os.path.join(path,"covid19_italy_province.csv"))

    if name is not None:
        os.replace(os.path.join(path, 'covid19_italy_region.csv'), os.path.join(path, check_csv_extension(name)))
        #in alternativa ci sarebbe anche la possibilità di usare "move" dal modulo shutil: from shutil import move
        #move(os.path.join(path, 'covid19_italy_region.csv'), os.path.join(path, check_csv_extension(name)))
        #uso move anzichè os.rename perche su windows non supporta la svorascrittura del file se già esistente

def read_covid_dataset(path=None, name=None):
    """
        Inserire sottoforma di stringa l'eventuale percorso e il nome del file (includere l'estensione .csv è opzionale)
        che si vuole caricare in un dataframe.
        Entrambi i valori sono opzionali.
        Se non si inserisce il percorso o il nome del file, di default verranno utilizzati la cartella di lavoro corrente
        ed il nome che kaggle assegna al file csv
        Esempio in ambiente UNIX:
            df=read_covid_dataset('/Users/user_name/Desktop', 'covid_dataset')
        Esempio in ambiente WINDOWS:
            df=read_covid_dataset('C:/Users/user_name/Desktop', 'covid_dataset')
            df=read_covid_dataset('C:\\Users\\user_name\\Desktop', 'covid_dataset')
    """
    if path is None:
        path = os.getcwd()
    if name is None:
        name = 'covid19_italy_region.csv'
    else:
        name = check_csv_extension(name)

    df = pd.read_csv(os.path.join(path, name),
                            names=['sno', 'data', 'stato', 'codice_regione', 'denominazione_regione', 'lat', 'long',
                                   'ricoverati_con_sintomi', 'terapia_intensiva', 'totale_ospedalizzati',
                                   'isolamento_domiciliare',
                                   'totale_positivi', 'nuovi_positivi', 'dimessi_guariti', 'deceduti', 'totale_casi',
                                   'casi_testati'],
                            header=0,
                            index_col='sno')

    df['data'] = pd.to_datetime(df['data'])
    df = df.fillna({'casi_testati': 0}, downcast='infer')
    # uso l'opzione downcast='infer' per far sì che in automatico assegni il tipo di dati appropriato
    df = df.drop(['stato', 'codice_regione', 'lat', 'long'], axis=1)

    def total_variation_of_positives(tot_pos):
        """
           Funzione che aggiunge al dataframe la colonna con la variazione giornaliera del numero toatale dei positivi
        """
        var_pos = []
        i = 0
        n_regions = 21
        while i < len(tot_pos):
            if i < 21:
                var_pos.append(0)
            else:
                x = tot_pos[i]
                y = tot_pos[i - n_regions]
                var_pos.append(x - y)
            i += 1
        return var_pos

    df['variazione_totale_positivi'] = total_variation_of_positives(df['totale_positivi'])
    unique_regions=df['denominazione_regione'].unique()
    df['denominazione_regione'] = df['denominazione_regione'].\
        replace(dict(zip(unique_regions, list(map(lambda x: x.capitalize(), unique_regions)))))

    return df