# Installation des packages nécessaires
!pip install requests pandas numpy matplotlib


# Récupération et nettoyage des données de l'API Scopus
import requests
import pandas as pd

def fetch_scopus_data(api_key, query, count=40):
    url = 'https://api.elsevier.com/content/search/scopus'
    params = {
        'apiKey': api_key,
        'query': query,
        'count': count
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
        data = response.json()
        if 'search-results' in data and 'entry' in data['search-results']:
            print(f"Nombre de résultats obtenus : {len(data['search-results']['entry'])}")
            return data['search-results']['entry']
        else:
            print("La structure de la réponse JSON ne contient pas les clés attendues.")
            return None
    
    except requests.exceptions.HTTPError as http_err:
        print(f'Erreur HTTP {response.status_code}: {response.reason}')
        print(response.text)
    except requests.exceptions.RequestException as req_err:
        print(f'Erreur de requête: {req_err}')
    except Exception as err:
        print(f'Erreur: {err}')

def parse_freetoread(value):
    if isinstance(value, list):
        return ', '.join([item['$'] for item in value])
    return value

def clean_and_save_data(entries, filename):
    if entries:
        df = pd.json_normalize(entries)
        
        if 'freetoread.value' in df.columns:
            df['freetoread.value'] = df['freetoread.value'].apply(parse_freetoread)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        print("DataFrame nettoyé")
        print(df)
        df.to_csv(filename, index=False)

# Récupérer, nettoyer et sauvegarder les données
api_key = 'f77d6f421b5670035ae2be3f652e2220'
query = 'KEY(scopus)'
filename = 'api_scopus_data.csv'
entries = fetch_scopus_data(api_key, query)
clean_and_save_data(entries, filename)




# Extraction et analyse des données à partir des DOI via l'API Elsevier
import requests
import pandas as pd
import xml.etree.ElementTree as ET
dois = [
    '10.1016/j.jmb.2008.10.026',
    '10.1038/nature04632',
    '10.1126/science.1133427'
]
api_key = 'f77d6f421b5670035ae2be3f652e2220'
def get_data_from_doi(doi):
    url = f'https://api.elsevier.com/content/article/doi/{doi}'
    headers = {'X-ELS-APIKey': api_key, 'Accept': 'application/xml'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()        
        root = ET.fromstring(response.content)
        return parse_xml(root)
    
    except requests.exceptions.HTTPError as err:
        print(f'Erreur HTTP lors de la récupération du DOI {doi}: {err}')
        return None
    
    except ET.ParseError as e:
        print(f'Erreur de parsing XML pour le DOI {doi}: {e}')
        return None
    
    except Exception as err:
        print(f'Erreur lors de la récupération du DOI {doi}: {err}')
        return None

def parse_xml(root):
    namespaces = {
        'dtd': 'http://www.elsevier.com/xml/svapi/article/dtd',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'prism': 'http://prismstandard.org/namespaces/basic/2.0/',
        'xocs': 'http://www.elsevier.com/xml/xocs/dtd'
    }

    data = {
        'doi': root.findtext('.//xocs:doi', namespaces=namespaces),
        'title': root.findtext('.//dc:title', namespaces=namespaces),
        'creator': root.findtext('.//dc:creator', namespaces=namespaces),
        'publicationName': root.findtext('.//prism:publicationName', namespaces=namespaces),
        'volume': root.findtext('.//prism:volume', namespaces=namespaces),
        'issue': root.findtext('.//prism:issueIdentifier', namespaces=namespaces),
        'pageRange': root.findtext('.//prism:pageRange', namespaces=namespaces),
        'coverDate': root.findtext('.//prism:coverDate', namespaces=namespaces),
        'citedby_count': root.findtext('.//xocs:citedby-count', namespaces=namespaces)
    }

    link_elements = root.findall('.//xocs:link', namespaces=namespaces)
    for link in link_elements:
        if link.get('rel') == 'scidir':
            data['doiLink'] = link.get('href')
            break

    return data

data_list = []
try:
    for doi in dois:
        data = get_data_from_doi(doi)
        if data:
            data_list.append(data)

    if data_list:
        df_xml = pd.DataFrame(data_list)
        df_xml_json = df_xml.to_json(orient='records')
        with open('scopus_data_from_dois.json', 'w', encoding='utf-8') as f:
            f.write(df_xml_json)
    else:
        print("Aucune donnée valide n'a été récupérée depuis les DOI.")

except requests.exceptions.HTTPError as err:
    print(f'Erreur HTTP lors de la requête à l\'API Elsevier: {err}')
except Exception as err:
    print(f'Erreur: {err}')








# Analyse des données de citations par année
import pandas as pd
import matplotlib.pyplot as plt

def analyze_data(df):
    if df is not None:
        # Calculer le nombre total de citations
        if 'citedby-count' in df.columns:
            df['citedby-count'] = pd.to_numeric(df['citedby-count'], errors='coerce').fillna(0).astype(int)
            total_citations = df['citedby-count'].sum()
            print(f"\nLe nombre total de citations pour toutes les publications: {total_citations}")

            # Les citations par année de publication 
        if 'prism:coverDate' in df.columns:
            df['coverYear'] = pd.to_datetime(df['prism:coverDate'], errors='coerce').dt.year
            citations_per_year = df.groupby('coverYear')['citedby-count'].sum()        
            print("\n Citations par année de publication :")
            for year, citations in citations_per_year.items():
                print(f"Année {year} : {citations} citations")

df = pd.read_csv('api_scopus_data.csv')
analyze_data(df)




#1.Calcul du nombre total de publications dans le dataset
def total_publications(df):
    if df is not None:
        total = len(df)
        print(f"\nLe nombre total de publications dans le dataset : {total}")
    else:
        print("Aucune donnée à analyser.")
total_publications(df)



#2.Calcul du nombre total de citations pour toutes les publications
def total_citations(df):
    if 'citedby-count' in df.columns:
        total_citations = df['citedby-count'].sum()
        print(f"\nLe nombre total de citations pour toutes les publications : {total_citations}")
    else:
        print("La colonne 'citedby-count' n'est pas présente dans le DataFrame.")
total_citations(df)



#3.Calcul de la moyenne des citations par publication
def average_citations(df):
    if 'citedby-count' in df.columns:
        average_citations = df['citedby-count'].mean()
        print(f"\nLes citations moyennes par publication : {average_citations:.2f}")
    else:
        print("La colonne 'citedby-count' n'est pas présente dans le DataFrame.")
average_citations(df)




#4.Identification des publications avec le plus de citations
def publications_most_citations(df, top_n=5):
    if 'citedby-count' in df.columns:
        top_publications = df.nlargest(top_n, 'citedby-count')[['dc:title', 'citedby-count']]
        print(f"\nles publications avec le plus de citations (Top {top_n}) :")
        print(top_publications)
    else:
        print("La colonne 'citedby-count' n'est pas présente dans le DataFrame.")
df = pd.read_csv('api_scopus_data.csv')
publications_most_citations(df)





#5.Analyse de la répartition des publications en accès libre
def publications_acces_libre(df):
    """Analyse la répartition des publications en accès libre."""
    if 'openaccessFlag' in df.columns:
        publications_open_access = df['openaccessFlag'].value_counts()
        print("\nRépartition des publications par statut d'accès libre :")
        print(publications_open_access)
    else:
        print("La colonne 'openaccessFlag' n'est pas présente dans le DataFrame.")
publications_acces_libre(df)




#6.Analyse de la répartition des publications par année
import pandas as pd
import matplotlib.pyplot as plt

def analyze_data(df):
    if df is not None:
        if 'prism:coverDate' in df.columns:
            df['coverYear'] = pd.to_datetime(df['prism:coverDate'], errors='coerce').dt.year
        if 'coverYear' in df.columns:
            publications_per_year = df.groupby('coverYear')['dc:title'].count().reset_index(name='Publications')
            print("\nRépartition des publications par année :")
            print(publications_per_year)
df = pd.read_csv('api_scopus_data.csv')

analyze_data(df)




# 7.Analyse de la répartition des publications par source
def publications_par_source(df):
    """Analyse la répartition des publications par source."""
    if 'prism:publicationName' in df.columns:
        publications_by_source = df['prism:publicationName'].value_counts().head(10)
        print("\nRépartition des publications par source (Top 10) :")
        print(publications_by_source)
    else:
        print("La colonne 'prism:publicationName' n'est pas présente dans le DataFrame.")
publications_par_source(df)




#8.Calcul de la corrélation entre le nombre de citations et les années de publication
def correlation_citations_annees(df):
    if 'citedby-count' in df.columns and ('prism:coverDate' in df.columns or 'prism:coverDisplayDate' in df.columns):
        if 'prism:coverDate' in df.columns:
            df['coverYear'] = pd.to_datetime(df['prism:coverDate'], errors='coerce').dt.year
        elif 'prism:coverDisplayDate' in df.columns:
            df['coverYear'] = pd.to_datetime(df['prism:coverDisplayDate'], errors='coerce').dt.year
        
        correlation = df[['coverYear', 'citedby-count']].corr().iloc[0, 1]
        print(f"\nCorrélation entre le nombre de citations et les années de publication : {correlation:.2f}")
    else:
        print("Les colonnes nécessaires ('citedby-count' et 'prism:coverDate' ou 'prism:coverDisplayDate') ne sont pas présentes dans le DataFrame.")
correlation_citations_annees(df)



#9.Analyse de la répartition des publications par ISSN
def publications_par_issn(df):
    """Analyse la répartition des publications par ISSN."""
    if 'prism:issn' in df.columns:
        publications_by_issn = df['prism:issn'].value_counts().head(10)
        print("\nRépartition des publications par ISSN (Top 10) :")
        print(publications_by_issn)
    else:
        print("La colonne 'prism:issn' n'est pas présente dans le DataFrame.")
publications_par_issn(df)



#10.Analyse de la répartition des publications par type de volume
def publications_par_volume(df):
    """Analyse la répartition des publications par type de volume."""
    if 'prism:volume' in df.columns:
        publications_by_volume = df['prism:volume'].value_counts().head(10)
        print("\nRépartition des publications par type de volume (Top 10) :")
        print(publications_by_volume)
    else:
        print("La colonne 'prism:volume' n'est pas présente dans le DataFrame.")
publications_par_volume(df)




#11. Analyse de la répartition des publications par type de source 
def publications_par_type_source(df):
    if 'prism:aggregationType' in df.columns:
        publications_by_aggregation_type = df['prism:aggregationType'].value_counts()
        print("\nRépartition des publications par type de source (Aggregation Type) :")
        print(publications_by_aggregation_type)
    else:
        print("La colonne 'prism:aggregationType' n'est pas présente dans le DataFrame.")
publications_par_type_source(df)








#12. Visualisation de la distribution des citations par publication
import matplotlib.pyplot as plt

def citations_distribution(df):
    if 'citedby-count' in df.columns:
        plt.figure(figsize=(10, 6))
        plt.hist(df['citedby-count'], bins=20, color='pink', edgecolor='black')
        plt.title('Les Citations par Publication')
        plt.xlabel('Nombre de Citations')
        plt.ylabel('Nombre de Publications')
        plt.grid(False)
        plt.show()
    else:
        print("La colonne 'citedby-count' n'est pas présente dans le DataFrame.")
citations_distribution(df)





#13 Analyse et visualisation de la répartition des publications par auteur
def publications_per_author(df):
    if 'dc:creator' in df.columns:
        publications_by_author = df['dc:creator'].value_counts()

        print("\nRépartition des publications par auteur :")
        print(publications_by_author.head(10))  

        plt.figure(figsize=(10, 6))
        publications_by_author.head(10).plot(kind='bar', color='pink')
        plt.xlabel('Auteur')
        plt.ylabel('Nombre de Publications')
        plt.title('Les Publications par Auteur')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("La colonne 'dc:creator' n'est pas présente dans le DataFrame.")
publications_per_author(df)






#14.Analyse et visualisation des citations par année
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('api_scopus_data.csv')

def citations_per_year(df):
    if 'citedby-count' in df.columns and 'prism:coverDate' in df.columns:
        df['coverYear'] = pd.to_datetime(df['prism:coverDate'], errors='coerce').dt.year
        
        citations_by_year = df.groupby('coverYear')['citedby-count'].sum()
        print("\nCitations par année :")
        print(citations_by_year)
        return citations_by_year  
    else:
        print("Les colonnes nécessaires ('citedby-count' et 'prism:coverDate') ne sont pas présentes dans le DataFrame.")
        return None
citations_by_year = citations_per_year(df)

if citations_by_year is not None:
    plt.figure(figsize=(10, 6))
    plt.bar(citations_by_year.index, citations_by_year.values, color='pink')
    plt.xlabel('Année de Publication')
    plt.ylabel('Nombre de Citations')
    plt.title('Citations par Année')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
else:
    print("Impossible de visualiser les données car les citations par année n'ont pas été calculées correctement.")




#15.Distribution des Citations par Publication
def plot_citations_distribution(df):
    if 'citedby-count' in df.columns:
        df_filtered = df[df['citedby-count'] > 0]
        plt.figure(figsize=(10, 6))
        plt.hist(df_filtered['citedby-count'], bins=20, color='pink', edgecolor='black')
        plt.xlabel('Nombre de Citations')
        plt.ylabel('Nombre de Publications')
        plt.title('Les Citations par Publication')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    else:
        print("La colonne 'citedby-count' n'est pas présente dans le DataFrame.")
plot_citations_distribution(df)








#16.Les Publications par Type de Volume
def plot_publications_by_volume(df):
    if 'prism:volume' in df.columns:
        publications_by_volume = df['prism:volume'].value_counts().head(5)
        plt.figure(figsize=(8, 8))
        plt.pie(publications_by_volume.values, labels=publications_by_volume.index, autopct='%1.1f%%', startangle=140)
        plt.title('Les Publications par Type de Volume')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    else:
        print("La colonne 'prism:volume' n'est pas présente dans le DataFrame.")
plot_publications_by_volume(df)




#17.Répartition des Publications par Auteur (Top 15)
def plot_publications_by_author(df):
    """Plot the distribution of publications by author."""
    if 'dc:creator' in df.columns:
        publications_by_author = df['dc:creator'].value_counts().head(15)
        plt.figure(figsize=(10, 6))
        plt.barh(publications_by_author.index, publications_by_author.values, color='pink')
        plt.xlabel('Nombre de Publications')
        plt.ylabel('Auteur')
        plt.title('Les Publications par Auteur (Top 10)')
        plt.gca().invert_yaxis()  
        plt.tight_layout()
        plt.show()
    else:
        print("La colonne 'dc:creator' n'est pas présente dans le DataFrame.")
plot_publications_by_author(df)





#18.Répartition des Publications par Source
def plot_publications_by_source(df):
    if 'prism:publicationName' in df.columns:
        publications_by_source = df['prism:publicationName'].value_counts().head(5)
        plt.figure(figsize=(8, 8))
        plt.pie(publications_by_source.values, labels=publications_by_source.index, autopct='%1.1f%%', startangle=140)
        plt.title('Les Publications par Source')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    else:
        print("La colonne 'prism:publicationName' n'est pas présente dans le DataFrame.")
plot_publications_by_source(df)






#19 Visualisation de la distribution des citations par type de publication
def distribution_citations_par_type(df):
    if 'citedby-count' in df.columns and 'prism:aggregationType' in df.columns:
        plt.figure(figsize=(10, 6))
        df_filtered = df[df['prism:aggregationType'].notna()]
        df_filtered['prism:aggregationType'] = df_filtered['prism:aggregationType'].str.lower()
        df_filtered['prism:aggregationType'].value_counts().plot(kind='bar', color='pink')
        plt.xlabel('Type de Publication')
        plt.ylabel('Nombre de Citations')
        plt.title('Les Citations par Type de Publication')
        plt.grid(axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("Les colonnes nécessaires ('citedby-count' et 'prism:aggregationType') ne sont pas présentes dans le DataFrame.")
distribution_citations_par_type(df)