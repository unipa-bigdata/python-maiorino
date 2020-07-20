def check_csv_extension(my_csv_file):
    """
        La funzione prende in input il nome assegnato ad un file e se non contiene l'estensione .csv, essa viene aggiunta.
    """
    if my_csv_file.endswith('.csv'):
        return my_csv_file
    else:
        return my_csv_file + '.csv'