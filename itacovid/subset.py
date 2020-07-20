from datetime import datetime

class RegionError (ValueError):
    pass

class MonthError (ValueError):
    pass

class PeriodError (ValueError):
    pass

def subset_by_region(df, *regions):
    """
        La funzione prende in input il dataframe e un numero varibile di regioni e ritorna il dataframe filtrato.
        Esempio:
        subset_by_region(region_df, 'Veneto', 'piemonte')
    """
    regions = list(map(lambda x: x.capitalize(), regions))
    regions_check = df['denominazione_regione'].unique()

    for region in regions:
        if region not in regions_check:
            raise RegionError('Uno o più nomi di Regione inseriti non sono corretti! Per favore inserisci '
                              'uno o più dei seguenti nomi:\n' + str(regions_check))

    return df[df.denominazione_regione.isin(regions)]

def subset_by_month(df, *months):
    """
        La funzione prende in input il dataframe e un numero varibile di mesi e ritorna il dataframe filtrato.
        Esempio:
        subset_by_region(region_df, 'marzo', 'aprile')
    """

    eng_month = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
    ita_month = ('Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre')
    ita_eng_month = dict(zip(ita_month, eng_month))
    months = map(lambda x: x.capitalize(), months)
    months_list = list(months)

    for month in months_list:
        if month not in ita_month:
            raise MonthError('Uno o più nomi di mesi inseriti non sono corretti! Per favore inserisci correttamente i mesi in italiano')

    translated_month = list(map(lambda x: ita_eng_month[x], months_list))
    #translated_month = map(lambda x: ita_eng_month[x], map(lambda x: x.capitalize(), months))

    return df[df.data.dt.strftime("%B").isin(translated_month)]

def subset_by_period(df, start, end):
    """
        La funzione prende in input il dataframe la data di inizio e di fine del periodo desiderato (estremi compresi).
        Il format da utilizzare è il seguente: 'gg/mm/aaaa'
        Esempio:
        subset_by_period(basic_df, '25/02/2020', '27/02/2020'):
    """
    start = datetime.strptime(start, '%d/%m/%Y').date()
    end = datetime.strptime(end, '%d/%m/%Y').date()
    min_date = df['data'].min().date()
    max_date = df['data'].max().date()

    if (start < min_date) or (end > max_date):
        raise PeriodError(f'Le date inserite sono fuori intervallo!\nInserisci una data compresa tra il '
                          f'{min_date.strftime("%d/%m/%Y")} e il {max_date.strftime("%d/%m/%Y")}')

    #Creo una maschera con dei valori booleani
    mask = (df['data'].dt.date >= start) & (df['data'].dt.date <= end)
    # uso l'attributo .dt per accedere alle componenti date/day/time altrimenti ritornerebbe il seguente errore: 'Series' object has no attribute 'date'

    return df[mask]
