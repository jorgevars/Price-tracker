# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
#import the libraries needed
from bs4 import BeautifulSoup
import os
import pandas as pd
import requests
import smtplib
from time import sleep


# %%
#Path to the CSV's with all the data
csv_file = os.path.dirname(os.path.abspath('')) +'\\Price tracker\\Price tracker.csv'
ids_file = os.path.dirname(os.path.abspath('')) +'\\Price tracker\\IDS.csv'

#Read the CSV's
data = pd.read_csv(csv_file)
ids = pd.read_csv(ids_file)

#Asignar los valores de correo y contraseña para el envio de correo
mail = data.iloc[0,0]         #mail usado en el csv
password = data.iloc[0,1]     #password usado en el csv


# %%
#Definir los headers para los requests
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.58'}


# %%
def send_mail(list_number, title, converted_price):
    #Inicializa los valores de correo
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    #Login al correo
    server.login(mail, password)

    #Envia un corro de error en el link
    if converted_price == 0:
        subject = 'Revisa el link!!'
        body = 'Revisa el link:\n\nYa que:\t\t' + title.strip() + '\n\nNo aparece el precio\n\n' + data['URL'][list_number]
    #Envia un correo con el artículo con precio menor al max_price
    else:
        subject = 'El precio bajo!!'
        body = ('Revisa el link:\n\nYa que:\t\t' + 
                title.strip() + '\n\nEsta en:\t$' + 
                '{:,.2f}'.format(converted_price) + 
                '\n\n' + data['URL'][list_number])    

    
    #Crea el correo
    msg = f"Subject: {subject}\n\n{body}"
    #Enviar correo
    server.sendmail(mail, mail,msg)

    print('El correo ha sido enviado')
    #Salida del server
    server.quit()


# %%
def check_price(list_number):
    #Descarga los dartos de la URL
    session = requests.Session()
    cookies = dict(cookies_are='working')
    page = requests.get(data["URL"][list_number], headers = headers, cookies = cookies)
    soup = BeautifulSoup(page.content, 'lxml')

    #Encontrar la URL principal
    end_of_URL = data["URL"][list_number].find("/")
    n = 3   #Para encontrar el tercer "/" indicando el fin de la URL principal 
    while end_of_URL >= 0 and n > 1:    #Encuentra la posición del final de la URL principal
        end_of_URL = data['URL'][list_number].find("/", end_of_URL + 1)
        n -= 1
    URL_principal = data['URL'][list_number][8:end_of_URL]

    #Encontrar la posición en el dataframe de ids
    id_loc = ids.loc[ids['URL'] == URL_principal].index[0]

    #Encontrar el precio de cada pagina
    if 'www.amazon.com' in URL_principal:
        title = soup.find(id = ids.iloc[id_loc, 1]).get_text().strip()
        try:
            price = soup.find(id = ids.iloc[id_loc, 2]).get_text().strip()
        except:
            price = "0"
    if (URL_principal == 'www.bestbuy.com.mx' or 
        URL_principal == 'www.mercadolibre.com.mx'):
        title = soup.find(class_ = ids.iloc[id_loc, 1]).get_text().strip()
        try:
            price = soup.find(class_ = ids.iloc[id_loc, 2]).get_text().strip()
        except:
            price = "0"
    
    #Convertir el precio en float
    converted_price = float(price.replace(',','').replace('$',''))

    #Imprime datos utiles
    print(URL_principal + "\t" + title + "\t$" + str(converted_price))
    
    #Enviar correo con instrucciones
    if(converted_price <= float(data["Max_price"][list_number])):
        send_mail(list_number,title,converted_price)


# %%
while True:
    for list_number in range(data['URL'].shape[0]):
        check_price(list_number)
    print("programa finalizado :)")
    #Repetir script cada hora
    #sleep(3600)
    #Repetir script cada día
    sleep(86400)
