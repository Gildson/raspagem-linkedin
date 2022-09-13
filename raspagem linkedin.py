from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import pandas as pd

import time

#Login do linkedin
browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
browser.get("https://www.linkedin.com/login")
time.sleep(3)
username = browser.find_element(By.ID, "username")
password = browser.find_element(By.ID, "password")

#Coloque o login de acesso
username.send_keys("trocar pelo login de acesso desejado")
#Coloque a senha de acesso
password.send_keys("senha do login")

time.sleep(2)
login_attempt = browser.find_element(By.CLASS_NAME, "login__form_action_container ").click()
time.sleep(5)

#entra nas conexões de 1º do usuário
link = 'https://www.linkedin.com/mynetwork/invite-connect/connections/'
browser.get(link)
src = browser.page_source

#Rola a tela até o final
last_height = browser.execute_script("return document.body.scrollHeight")

for i in range(3):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(5)

    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

soup = BeautifulSoup(src, 'html.parser')

#Pega todos os links das conexões
all_link = []
links = soup.find_all('li', attrs={'class': 'mn-connection-card artdeco-list'})
for link in links:
   nome = link.find('a')
   all_link.append(nome.get('href'))

#Função que pega os dados
def dados_conexao(url):
  link = 'https://www.linkedin.com' + url
  browser.get(link)

  #Devido a tela da conexão ser maior, utilizei outro trecho de código para rolar a tela	
  start = time.time()
  initialScroll = 0
  finalScroll = 1000
  
  while True:
    browser.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
    # this command scrolls the window starting from
    # the pixel value stored in the initialScroll 
    # variable to the pixel value stored at the
    # finalScroll variable
    initialScroll = finalScroll
    finalScroll += 1000
  
    time.sleep(3)
  
    end = time.time()
    if round(end - start) > 20:
      break
  
  time.sleep(5)
  src = browser.page_source
  soup1 = BeautifulSoup(src, 'lxml')

  dados_da_conexao = []

  #Pegar informações das conexões
  name_div_nome = soup1.find('div', attrs={'class': "mt2 relative"})
  name_perfil = name_div_nome.find('h1').text
  local_cidade = name_div_nome.find('div', attrs={'class': "pv-text-details__left-panel pb2"})
  local = local_cidade.find('span').text.replace('\n', '')
  describe = name_div_nome.find('div', attrs={'class': "text-body-medium break-words"}).text.replace('\n', '')
  cargos = name_div_nome.find('span', attrs={'class': 'pv-text-details__right-panel-item-text hoverable-link-text break-words text-body-small t-black'})
  cargo_atual = cargos.find('div').get_text().replace('\n', '')

  
  linkedin_empresas = []
  experiencia = soup1.find('div', attrs={'id': 'experience'}).parent
  experi = experiencia.find('div', attrs={'class': 'pvs-list__outer-container'})
  
  #Pegar informações das empresa
  expe = experi.find_all('a')
  for empresa in expe:
    link_empresa = empresa.get('href')
    browser.get(link_empresa)
    src1 = browser.page_source
    soup2 = BeautifulSoup(src1, 'lxml')
    company = soup2.find('div', {'class': 'block mt2'})
    nome_company = company.find('h1').title
    setora_company = company.find('div', {'class': 'org-top-card-summary-info-list t-14 t-black--light'})
    setor_company = setora_company.find('div', {'class': 'org-top-card-summary-info-list__info-item'}).text
    lo_company = company.find('div', {'class': 'inline-block'})
    local_company = lo_company.find('div', {'class': 'org-top-card-summary-info-list__info-item'}).text
    cola_company = soup2.find('div', {'class': 'mt1'})
    link_div_pessoas = cola_company.find('div', {'class': 'org-top-card-secondary-content__connections display-flex align-items-center mt4 mb1'})
    link_colab_company = link_div_pessoas.find('a', {'class': 'ember-view org-top-card-secondary-content__see-all-link'})
    link_colaboradores_company = link_colab_company.get('href')
    for colaboradores in link_colaboradores_company:
      browser.get(link_empresa)
      
      last_height_col = browser.execute_script("return document.body.scrollHeight")
      for j in range(3):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(5)

        new_height_col = browser.execute_script("return document.body.scrollHeight")
        if new_height_col == last_height_col:
          break
        last_height_col = new_height_col
    
      src2 = browser.page_source
      soup3 = BeautifulSoup(src2, 'lxml')

      all_link_company = []
      links = soup.find_all('li', attrs={'class': 'reusable-search__result-container '})
      for link in links:
        nome_col_company = link.find('a')
        all_link_company.append(nome_col_company.get('href'))
    
    linkedin_empresas.append([nome_company, setor_company, local_company, all_link_company])

  dados_da_conexao.append([name_perfil, local, describe, cargo_atual, linkedin_empresas])
  return dados_da_conexao

#Cria o dataframe
colunas = [
    'Nome da conexão',
    'Local',
    'Descrição',
    'Cargo atual',
    'Dados das empresas'
]

Dataset_linkedin = pd.DataFrame(columns=colunas)

#Chama a função que faz a varedura do linkedin e adiciona no dataframe criado
for i in range(len(all_link)):
    dataset_linkedin.loc[-1] = dados_conexao(all_link[i])
    dataset_linkedin.index = dataset_linkedin.index + 1
    dataset_linkedin = dataset_linkedin.sort_index()
