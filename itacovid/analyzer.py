import os
import json
import pandas as pd
from .check_csv_extension import check_csv_extension
from datetime import datetime
import pprint
import copy

class DuplicatedStringError (ValueError):
    pass

class Analyzer():
    """
    Definire il valore da assegnare ai seguenti attributi:
        1. path_to_results: il percorso in cui si vuole creare il file con i risultati delle analisi
        2. name: il nome che si vuole assegnare al file con i risultati delle analisi
        (includere l'estensione .csv è opzionale)
    se non si inseriscono valori, verranno utilizzate le impostazioni di default e il percorso coinciderà con quello
    in cui si sta lavorando.
    """
    def __init__(self, path_to_results = None, name_to_results = None):
         self._path_to_results = path_to_results
         self._name_to_results = name_to_results

    @property
    def path_to_results(self):
        if self._path_to_results is None:
            return os.getcwd()
        else:
            return self._path_to_results

    @path_to_results.setter
    def path_to_results(self, value):
        self._path_to_results = value

    @property
    def name_to_results(self):
        if self._name_to_results is None:
            return 'covid19_result.csv'
        else:
            return self._name_to_results

    @name_to_results.setter
    def name_to_results(self, value):
        self._name_to_results = check_csv_extension(value)
    

    def store_config(self):
        """
            Metodo da utilizzare per creare un file nascosto .config.json con all'interno un dizionario contenente:
                - il percorso al file in cui verranno memorizzati i risultati delle analisi
                - il nome del file in cui verranno memorizzati i risultati delle analisi

            Il percorso in cui vinene memorizzato il file di configurazone coinciderà con quello in cui si sta lavorando.
            Attenzione, se il file già esiste, verrà sovrascritto!
        """

        path_to_config_file = os.getcwd()
        my_data={'path_to_results': self.path_to_results, 'name_to_results': self.name_to_results}
        dir_config = os.path.join(path_to_config_file, '.config.json')
        with open(dir_config, 'w') as f_obj:
            json.dump(my_data, f_obj)

    def load_config(self):
        """
            Metodo da utilizzare per caricare in memoria le variabili del percorso e il nome del file
            in cui verranno memorizzati i risultati delle analisi, contenute all'interno del file .config.json

            Se non viene trovato il file .config.json comparirà un messaggio di errore. Si prega di generare il file con
            il metodo store_confg qualora non fosse già stato istanziato.
        """

        path_to_config_file = os.getcwd()
        dir_config = os.path.join(path_to_config_file, '.config.json')
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
        period = str(df['data'].max().date().strftime("%d/%m/%Y") + " - " + df['data'].min().date().strftime("%d/%m/%Y"))
        regions = df['denominazione_regione'].unique()
        column_list = list(df.columns[2:-1])

        dict_with_results = {r: {'valori massimi': dict(df.loc[df.denominazione_regione == r, column_list].max()),
                                 'valori minimi': dict(df.loc[df.denominazione_regione == r, column_list].min()),
                                 'valori medi': dict(df.loc[df.denominazione_regione == r, column_list].mean()),
                                 'deviazione standard': dict(df.loc[df.denominazione_regione == r, column_list].std())} for r in regions}

        dict_with_results['periodo'] = period

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

            Se il valore inserito per la memorizzazione dei dati è gia presente o è uguale all'header, comparirà un messaggio di errore!
        """
        try:
            if my_unique_string is None:
                my_unique_string = datetime.now()
            # se il file con i risultati già esiste verifico che il valore di unique_identification non sia già inserito!!!
            elif os.path.isfile(os.path.join(self.path_to_results, self.name_to_results)):
                unique_identification_list = pd.read_csv(os.path.join(self.path_to_results, self.name_to_results), usecols=[0], skiprows=[0], squeeze=True).unique()
                if my_unique_string in unique_identification_list:
                    raise DuplicatedStringError
            # se il file con i risultati NON esiste verifico che il valore di unique_identification sia diverso dalla stringa 'unique_identification'
            elif my_unique_string == 'unique_identification':
                raise DuplicatedStringError

            #effettuo una copia del dizionario per non modificare quello originale fornito dall'utente
            dictionary = copy.deepcopy(my_dict)

            period = dictionary.pop('periodo')
            # faccio il pivoting di un livello dell'indice
            df = pd.DataFrame(dictionary).T.stack().apply(pd.Series)
            df = df.unstack(level=-1)
            # assegno il nome alla colonna regioni
            new_index_name = df.index.set_names('regioni') # --> in alternativa new_index_name=df3.index.rename('regioni')
            df = df.reindex(new_index_name)
            df = df.assign(periodo=period, unique_identification=my_unique_string).set_index(['periodo', 'unique_identification'], append=True).\
                swaplevel(0, 2)
                # in alternativa
                # reorder the levels
                # df.reorder_levels([1, 2, 0])

            #se il file esiste deve appendere i risultati
            if not os.path.isfile(os.path.join(self.path_to_results, self.name_to_results)):
                df.to_csv(os.path.join(self.path_to_results, self.name_to_results), mode='a')
            else:
                df.to_csv(os.path.join(self.path_to_results, self.name_to_results), mode='a', header=False)

        except DuplicatedStringError:
            print('Hai inserito un valore già esistente!\nL\'identificativo per la memorizzazione deve essere univoco o comunque diverso dall\'header.\nSi consiglia di utilizzare i valori di default.' )
        else:
            return print('Salvataggio riuscito correttamente!')

    def load_results(self):
        """
            La funzione permette di caricare i risultati memorizzati nel file .csv in un dataframe
        """
        return pd.read_csv(os.path.join(self.path_to_results, self.name_to_results), index_col=[0, 1, 2], header=[0, 1])


analyzer=Analyzer()

