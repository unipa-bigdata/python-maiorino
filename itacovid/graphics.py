import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class NotEnoughRegionsError(ValueError):
    pass

class Graphics():

    def __init__(self):
        pass

    @staticmethod
    def __data_mining_for_barh_and_pie(df):
        """
           1. Filtro i dati alla data di ultimo aggiornamento;
           2. Mantengo solo le colonne d'interesse;
           3. Setto l'indice sulla colonna denomianzione_regione;
           4. Ordino in maniera discendente in base al totale dei casi;
        """
        df = df[df.data == df.data.max()]
        df = df[['denominazione_regione', 'totale_positivi', 'dimessi_guariti', 'deceduti', 'totale_casi']]
        df = df.set_index('denominazione_regione').sort_values('totale_casi', ascending=False)

        return df

    @classmethod
    def bar(cls, df):
        """
           Prende in input un dataframe e ritorna un grafico a barre con il numero dei deceduti e il totale dei casi,
           suddivisi per mese.
        """
        grouped_df=df.groupby([df['data'].dt.strftime("%m"), 'denominazione_regione'])
        monthly_df=grouped_df.agg({'deceduti': max, 'totale_casi': max}).groupby(['data']).\
            agg({'deceduti': sum, 'totale_casi': sum})

        def sub_row(row):
            """
               Effettua una trasformazione ai dati contenuti nel dataframe sottraendo al valore di ogni riga quello
               della riga riferita al mese precedente per far si che i valori si riferiscano esclusivamente al mese
               indicato e non abbiano dati riferiti anche ai mesi precedenti:
            """
            new_row = [row[0]]
            for i in range(1, row.count()):
                new_row.append(row[i] - row[i - 1])
            return new_row

        monthly_df['deceduti'] = sub_row(monthly_df['deceduti'])
        monthly_df['totale_casi'] = sub_row(monthly_df['totale_casi'])

        labels = monthly_df.index.to_numpy()
        deceased = monthly_df['deceduti'].to_numpy()
        total_cases = monthly_df['totale_casi'].to_numpy()

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        ax.bar(x - width / 2, deceased, width, label='Deceduti')
        ax.bar(x + width / 2, total_cases, width, label='Totale casi')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_title('Deceduti e totale dei casi suddivisi per mese')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_xlabel('Mesi')
        ax.legend()

        fig.tight_layout()
        plt.close(fig)
        return fig

    @classmethod
    def barh(cls, df):
        """
           Prende in input un dataframe e ritorna un grafico a barre orizzantali con i seguenti dati per ogni Regione
           presente nel dataframe:
            - totale_positivi
            - dimessi_guariti
            - deceduti
        """
        df = cls.__data_mining_for_barh_and_pie(df)
        fig = df.plot.barh(y=['totale_positivi', 'dimessi_guariti', 'deceduti'], stacked=True, figsize=(15, 8))
        plt.close(fig.figure)
        #con plt.close evito di stampare due volte la stessa figura, lascio che stampi la get_figure()
        fig = fig.get_figure()
        return fig

    @classmethod
    def line(cls, df):
        """
           Prende in input un dataframe e ritorna un grafico a linee con i seguenti dati per singolo giorno
           presente nel dataframe:
            - totale_positivi
            - dimessi_guariti
            - deceduti
        """
        fig = df.groupby('data').agg(sum).loc[:,['dimessi_guariti', 'deceduti', 'totale_positivi']].plot(kind='line', figsize=(10,5))
        plt.close(fig.figure)
        #con plt.close evito di stampare due volte la stessa figura, lascio che stampi la get_figure()
        fig = fig.get_figure()
        return fig

    @classmethod
    def line_nuovi_positivi(cls, df):
        """
           Prende in input un dataframe e ritorna un grafico con l'andamento dei nuovi positivi per ogni giorno.
        """
        fig = df.groupby('data').agg(sum).plot(kind='line', y=['nuovi_positivi'], figsize=(10,5), color='m', linestyle='dashdot', grid=True)
        plt.close(fig.figure)
        #con plt.close evito di stampare due volte la stessa figura, lascio che stampi la get_figure()
        fig = fig.get_figure()
        return fig

    @classmethod
    def line_variazione_totale_positivi(cls, df):
        """
           Prende in input un dataframe e ritorna un grafico con l'andamento dei nuovi positivi per ogni giorno.
        """
        with plt.style.context('dark_background'):
            fig = df.groupby('data').agg(sum).plot(kind='line', y=['variazione_totale_positivi'], figsize=(10,5),
              color='orange', linestyle='dotted', linewidth=2, grid=True)
            plt.close(fig.figure)
            # con plt.close evito di stampare due volte la stessa figura, lascio che stampi la get_figure()
            fig = fig.get_figure()
            return fig

    @classmethod
    def pie_three_most_affected_regions(cls, df):
        """
           Prende in input un dataframe e per le prime tre Regioni più colpite in base al totale dei casi ritorna
           un grafico a torta  con le percentuali dei seguenti campi:
            - totale_positivi
            - dimessi_guariti
            - deceduti
        """
        if len(df['denominazione_regione'].unique())<3:
            raise NotEnoughRegionsError('Not enough Regions available in the dataframe! Please use another dataframe')

        df = cls.__data_mining_for_barh_and_pie(df)
        df = df.head(3).T.drop('totale_casi',axis=0)

        my_colors = ['#227c9d', '#17c3b2', '#ffcb77']
        fig = df.plot.pie(subplots=True, figsize=(25, 10), explode=(0, 0, 0.15), autopct='%1.1f%%', shadow=True,
                       colors=my_colors, fontsize=17, labeldistance=None)
        plt.close(fig[0].figure)
        fig = fig[0].get_figure()
        return fig

    @classmethod
    def nested_pie_three_most_affected_regions(cls, df):
        """
           Prende in input un dataframe e per le prime tre Regioni più colpite in base al totale dei casi ritorna
           un grafico a torta  nidificato con le percentuali dei seguenti campi:
            - totale_positivi
            - dimessi_guariti
            - deceduti
        """
        if len(df['denominazione_regione'].unique()) < 3:
            raise NotEnoughRegionsError('Not enough Regions available in the dataframe! Please use another dataframe')

        df = cls.__data_mining_for_barh_and_pie(df)
        nested_df=df.head(3)
        total_cases = nested_df['totale_casi'].to_numpy()
        labels_cases = nested_df.columns[:-1].tolist()
        labels_regions = nested_df.index.tolist()
        values=nested_df[labels_cases].to_numpy().flatten()
        #flatten converte il 2D array in 1D array

        #se avessi voluto usare le espressioni regolari:
        #import re
        #valori = list(map(lambda x: int(x), re.findall('\d+', str(nested_df[labels_casi].values.tolist()))))

        # Definisco i colori da utilizzare
        regions_colors = ['#874D9A', '#EE4266', '#FFD23F']
        cases_colors = ['#F18F01', '#048BA8', '#2E4057'] * 3

        # Definisco le impostazioni del grafico
        plt.pie(total_cases, startangle=90, colors=regions_colors, labels=labels_regions, frame=True, shadow=True)
        plt.pie(values, colors=cases_colors, radius=0.75, startangle=90, shadow=True)
        centre_circle = plt.Circle((0, 0), 0.5, color='black', fc='white', linewidth=0)
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        plt.axis('equal')
        plt.tight_layout()

        # Definisco la legenda
        plt.legend(labels_regions + labels_cases, bbox_to_anchor=(1.2, 1), shadow=True)
        # come primo argomento di plt.legend() ho inserito una lista contenente il nome delle etichette per evitare che vengano assegnate automaticamente

        plt.close(fig)
        return fig