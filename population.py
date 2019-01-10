import requests
import unicodedata
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from pprint import pprint

def ukraine_population():
    '''Динамика численности населения Украины по годам'''

    searchtext = 'https://ru.wikipedia.org/wiki/%D0%9D%D0%B0%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5_%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D1%8B'
    result = requests.get(searchtext)
    soup = BeautifulSoup(result.text, features="html.parser")

    tables = soup.find_all('table')
    tbody = tables[1].find('tbody')
    th = tbody.find_all('th')
    td = tbody.find_all('td')

    result_pop = [int(unicodedata.normalize('NFKC', item.get_text()).strip("\n↗↘").replace(" ", "")) for item in td
                  if unicodedata.normalize('NFKC', item.get_text()).strip("\n↗↘") != '']

    _, *years = [item.get_text()[0:item.get_text().find('[')]
                 for item in th if item.get_text().strip("\n") != '']

    population = pd.DataFrame({'year': years, 'population': result_pop}) # подготовлено к загрузке в БД
    return population

def regions_population():
    '''Динамика численности наличного населения по областям'''

    searchtext = 'https://ru.wikipedia.org/wiki/%D0%9D%D0%B0%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5_%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D1%8B'
    result = requests.get(searchtext)
    soup = BeautifulSoup(result.text, features="html.parser")

    tables = soup.find_all('table')
    tbody = tables[4].find('tbody')
    rows = tbody.find_all('tr')
    th = rows[0].find_all('th')

    years = [item.get_text()[0:item.get_text().find('[')] if item.get_text().find('[') > 0
           else item.get_text().strip("\n") for item in th[1:] ]    #   ключи для словаря DataFrame

    d = {'year':years}
    for i in range(len(rows[1:])):
        buffer = rows[i].find_all('td')
        if len(buffer) > 0:
            if buffer[0].get_text().find('[') > 0:
                region = buffer[0].get_text()[0:buffer[0].get_text().find('[')]
            else:
                region = buffer[0].get_text().strip('\n')
        for j in range(len(buffer[1:])):
            if buffer[j+1].get_text() == '':
                d.setdefault(region, []).append(np.nan)
            else:
                d.setdefault(region, []).append(float(buffer[j+1].get_text().replace(',', '.').strip('\n')))
    regions = pd.DataFrame(d) #   подготовлено к загрузке в БД
    return regions

def gender_population():
    '''Продолжительность жизни мужчин и женщин'''

    searchtext = 'https://ru.wikipedia.org/wiki/%D0%9D%D0%B0%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5_%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D1%8B'
    result = requests.get(searchtext)
    soup = BeautifulSoup(result.text, features="html.parser")

    tables = soup.find_all('table')
    tbody = tables[10].find('tbody')
    rows = tbody.find_all('tr')
    th = rows[0].find_all('th')

    headers = ["year", "male", "female"]

    d = dict()
    for i in range(len(headers)):
        if i == 0:
            value = [int(item.get_text()[0:item.get_text().find('[')]) if item.get_text().find('[') > 0
                     else item.get_text().strip("\n") for item in th[1:]]
        else:
            value = [float(item.get_text().replace(',', '.').strip("\n")) for item in rows[i].find_all('td')[1:]]
        
        d.setdefault(headers[i], value)

    gender = pd.DataFrame(d) #   подготовлено к загрузке в БД
    return gender

def born_died_population():
    '''Смертность и рождаемость населения Украины'''

    searchtext = 'http://www.ukrstat.gov.ua/operativ/operativ2007/ds/nas_rik/nas_u/nas_rik_u.html'  # официальная статистика
    result = requests.get(searchtext)
    soup = BeautifulSoup(result.text, features="html.parser")
    
    tables = soup.find('table', {'id':'table4'})
    rows = tables.find_all('tr')
    pop = [['year'], ['born'], ['died']]
    for i in range(1, len(rows)):
        pop[0].append(rows[i].find_all('td')[0].get_text().strip('\n')[:4])
        pop[1].append(float(rows[i].find_all('td')[1].get_text().replace(',','.').strip('\n')))
        pop[2].append(float(rows[i].find_all('td')[3].get_text().replace(',','.').strip('\n')))

    d = dict()
    for i in range(len(pop)):
        d[pop[i][0]] = pop[i][1:]

    born_died = pd.DataFrame(d)  #   подготовлено к загрузке в БД
    return born_died

if __name__== '__main__':
    pprint(regions_population())
