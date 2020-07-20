import os
import json
import pandas as pd
from .check_csv_extension import check_csv_extension
from datetime import datetime
import pprint
import copy

class Analysis():
    """
    Definire il valore da assegnare ai seguenti attributi:
        1. path_to_results: il percorso in cui si vuole creare il file con i risultati delle analisi
        2. name: il nome che si vuole assegnare al file con i risultati delle analisi
        (includere l'estensione .csv è opzionale)
    se non si inseriscono valori, verranno utilizzate le impostazioni di default e il percorso coinciderà con quello
    in cui si sta lavorando.
    """
    def __init__(self, path_to_results = None, name_to_results = None):
         self.path_to_results = path_to_results
         self.name_to_results = name_to_results

    def store_config(self, path_to_config_file=None):
        """
            Metodo da utilizzare per creare un file config.json con all'interno un dizionario contenente:
                - il percorso al file in cui verranno memorizzati i risultati delle analisi
                - il nome del file in cui verranno memorizzati i risultati delle analisi

            Il metodo prende in ingresso un parametro opzionale:
                1. path_to_config_file: il percorso in cui si vuole creare il file config.json;
            se non si inseriscono valori, verranno utilizzate le impostazioni di default e il percorso coinciderà con quello
            in cui si sta lavorando.

            Esempio:
                set_access_results_config(path_to_config_file='/Users/user_name/Desktop/covid')
        """
        if self.name_to_results is None:
            self.name_to_results = 'covid19_result.csv'
        else:
            self.name_to_results = check_csv_extension(self.name_to_results)

        if self.path_to_results is None:
            self.path_to_results = os.getcwd()

        if path_to_config_file is None:
            path_to_config_file = os.getcwd()

        my_data={'path_to_results': self.path_to_results, 'name_to_results': self.name_to_results}
        dir_config = os.path.join(path_to_config_file, 'config.json')
        with open(dir_config, 'w') as f_obj:
            json.dump(my_data, f_obj)

    def load_config(self, path_to_config_file=None):
        """
            Metodo da utilizzare per caricare in memoria le variabili del percorso e il nome del file
            in cui verranno memorizzati i risultati delle analisi, contenute all'interno di config.json

            Il metodo prende in ingresso un parametro opzionale:
                1. path_to_config_file: il percorso in cui è memorizzato il file config.json;
            se non si inseriscono valori, verranno utilizzate le impostazioni di default e il percorso coinciderà con quello
            in cui si sta lavorando.

            Se non viene trovato il file config.json comparirà un messaggio di errore. Si prega di controllare la correttezza del
            percorso o altrimenti di generare il file con il metodo set_confg qualora non fosse già stata istanziato.
        """
        if path_to_config_file is None:
            path_to_config_file = os.getcwd()

        dir_config = os.path.join(path_to_config_file, 'config.json')
        with open(dir_config) as f_obj:
            my_data = json.load(f_obj)

        self.path_to_results = my_data['path_to_results']
        self.name_to_results = my_data['name_to_results']

    def analyze(self, df):
        """
            La funzione prende in input il dataframe definito dall'utente e resituisce un dizionario con:
                -valori massimi;
                -valori minimi;
                -valori medi;
                -deviazione standard
            delle principali serie contenute all'interno del dataframe e raggruppando i dati per Regione.
        """
        periodo = str(
            df['data'].max().date().strftime("%d/%m/%Y") + " - " + df['data'].min().date().strftime("%d/%m/%Y"))
        regioni = df['denominazione_regione'].unique()
        column_list = list(df.columns[4:])

        dict_with_results = {r: {'valori massimi': dict(df.loc[df.denominazione_regione == r, column_list].max()),
                                 'valori minimi': dict(df.loc[df.denominazione_regione == r, column_list].min()),
                                 'valori medi': dict(df.loc[df.denominazione_regione == r, column_list].mean()),
                                 'deviazione standard': dict(df.loc[df.denominazione_regione == r, column_list].std())} for r in regioni}

        dict_with_results['periodo'] = periodo

        return dict_with_results

    def print_results(self, dictionary):
        """
            La funzione prende in input il dizionario con i risultati ottenuti dalla funzione analyze e restituisce una stampa dello stesso
            sottoforma di stringa formattata.
        """
        return pprint.pprint(dictionary)

    def save_results(self, my_dict, my_unique_string=None):
        """
            La funzione permette di memorizzare i risultati ottenuti in un file .csv prendendo in input il dizionario con i risultati ottenuti
            dalla funzione analyze e in via opzionale il valore univoco che si vuole assegnare ai dati, se non specificato assegna il datatime dell'istante
            in cui si richiama la funzione.
        """
        if my_unique_string is None:
            my_unique_string = datetime.now()
        #else: inserire un controllo per verificare che quel valore non sia già inserito

        #effettuo una copia del dizionario per non modificare quello originale fornito dall'utente
        dictionary = copy.deepcopy(my_dict)
        periodo = dictionary.pop('periodo')
        df = pd.DataFrame(dictionary).T.stack().apply(pd.Series)
        # faccio il pivoting di un livello dell'indice
        df = df.unstack(level=-1)
        # assegno il nome alla colonna regioni
        new_index_name = df.index.set_names('regioni') # --> in alternativa new_index_name=df3.index.rename('regioni')
        df = df.reindex(new_index_name)
        df = df.assign(periodo=periodo, unique_identification=my_unique_string).set_index(['periodo', 'unique_identification'], append=True).\
            swaplevel(0, 2)
            # in alternativa
            # reorder the levels
            # df.reorder_levels([1, 2, 0])

        #se il file esiste deve appendere i risultati
        if not os.path.isfile(os.path.join(self.path_to_results, self.name_to_results)):
            df.to_csv(os.path.join(self.path_to_results, self.name_to_results), mode='a')
        else:
            df.to_csv(os.path.join(self.path_to_results, self.name_to_results), mode='a', header=False)

        return print('Salvataggio riuscito correttamente!')

    def load_results(self):
        """
            La funzione permette di caricare i risultati memorizzati nel file .csv in un dataframe
        """
        return pd.read_csv(os.path.join(self.path_to_results, self.name_to_results), index_col=[0, 1, 2], header=[0, 1])


analysis=Analysis()

