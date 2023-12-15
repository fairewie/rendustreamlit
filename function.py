
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from datetime import datetime
# Gestion d'une base de données


from sqlalchemy import distinct
import sqlalchemy as db

class DataBase():
    def __init__(self, name_database='yugioh'):
        self.name = name_database
        self.url = f"sqlite:///{name_database}.db"
        self.engine = db.create_engine(self.url)
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()
        self.table = self.engine.table_names()


    def create_table(self, name_table, **kwargs):
        colums = [db.Column(k, v, primary_key = True) if 'id_' in k else db.Column(k, v) for k,v in kwargs.items()]
        db.Table(name_table, self.metadata, *colums)
        self.metadata.create_all(self.engine)
        print(f"Table : '{name_table}' are created succesfully")

    def read_table(self, name_table, return_keys=False):
        table = db.Table(name_table, self.metadata, autoload=True, autoload_with=self.engine)
        if return_keys:
            return table.columns.keys()
        else:
            return table

    def add_row(self, name_table, **kwarrgs):
        name_table = self.read_table(name_table)

        stmt = (
            db.insert(name_table).
            values(kwarrgs)
        )
        self.connection.execute(stmt)
        print(f'Row id added')


    def delete_row_by_id(self, table, id_):
        name_table = self.read_table(name_table)

        stmt = (
            db.delete(name_table).
            where(table.c.id_ == id_)
            )
        self.connection.execute(stmt)
        print(f'Row id {id_} deleted')

    def select_table(self, name_table):
        name_table = self.read_table(name_table)
        stm = db.select([name_table])
        return self.connection.execute(stm).fetchall()

    def select_distinct_dates(self, name_table):
        name_table = self.read_table(name_table)
        date_column = name_table.columns.date
        stmt = db.select([distinct(date_column)])
        results = self.connection.execute(stmt).fetchall()
        unique_dates = [str(result[0]) for result in results]

        return unique_dates
    
    def select_data_for_date(self, name_table, selected_date):
        table = self.read_table(name_table)
        stmt = db.select([table]).where(table.c.date == selected_date)
        result = self.connection.execute(stmt)
        return [dict(row) for row in result]
    
    
database = DataBase(name_database='yugioh')



try:
    database.create_table('carte_yugioh',
                          cid=db.String,
                          nom=db.String,
                          image=db.String,
                          description=db.String,
                          attaque=db.String,
                          defense=db.String,
                          attribut=db.String,
                          niveau=db.String,
                          date = db.String
                          )
except:
    print("Erreur lors de la création de la table")

chrome_options = Options()
chrome_options.add_argument('--headless')  # Active le mode headless
chrome_options.add_argument('--disable-gpu')  # Désactive le rendu GPU (utile en mode headless)


driver = webdriver.Chrome(options=chrome_options)

BASE_URL  = f"https://www.db.yugioh-card.com/yugiohdb/card_list.action?clm=3&wname=CardSearch"
driver.get(BASE_URL)

ListeDeck = driver.find_element(By.ID, "update_list")
ListeLienDeck = ListeDeck.find_elements(By.CLASS_NAME, "t_row")
Carddata = {}

def create_dynamic_table_name():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f'collecte_{timestamp}'

datetemp = create_dynamic_table_name()


def collectInfo(datetemp):
    local_database = DataBase(name_database='yugioh')

    cardlist = driver.find_element(By.ID, "card_list")
    cartes = cardlist.find_elements(By.CLASS_NAME, "t_row")
    for carte in cartes:
        try:
            nom = carte.find_element(By.CLASS_NAME, "card_name").text                            
        except:
            nom = None

        try:
            image = carte.find_element(By.TAG_NAME, "img").get_attribute("src")          
        except:
            image = None
        
        try:
            description = carte.find_element(By.CLASS_NAME, "box_card_text").text         
        except:
            description = None
        
        try:
            attaque = carte.find_element(By.CLASS_NAME, "atk_power").text      
        except:
            attaque = None

        try:
            defense =  carte.find_element(By.CLASS_NAME, "def_power").text         
        except:
            defense = None

        try:
            attribut = carte.find_element(By.CLASS_NAME, "box_card_attribute").text         
        except:
            attribut = None

        try:
            niveau = carte.find_element(By.CLASS_NAME, "box_card_level_rank").text        
        except:
            niveau = None


        cidAll = carte.find_element(By.CLASS_NAME, "link_value").get_attribute("value")
        cid = cidAll.split("cid=")[1]
        Carddata[cid] =  { 'nom' :nom,  'image'  :image, 'description' :description, 'attaque' :attaque, 'defense' :defense, 'attribut' :attribut, 'niveau' :niveau ,'date' : datetemp}
        try:
            local_database.add_row('carte_yugioh', cid=cid, nom=nom, image=image, description=description, attaque=attaque, defense=defense, attribut=attribut, niveau=niveau,date = datetemp)
        except Exception as e:
            print(f"Une erreur s'est produite lors de l'ajout de la ligne dans la base de données: {e}")

def donner(nb_page=1):
    datetemp = create_dynamic_table_name()
    for i in range(nb_page):
        ListeDeck = driver.find_element(By.ID, "update_list")
        ListeLienDeck = ListeDeck.find_elements(By.CLASS_NAME, "t_row")
        try:
            driver.execute_script("arguments[0].scrollIntoView();", ListeLienDeck[i])
            ListeLienDeck[i].click()
            time.sleep(2)
            collectInfo(datetemp)
            driver.back()
        except Exception as e:
            print(f"Une erreur s'est produite lors du clic sur le lien {i}: {e}")
        time.sleep(2)

    return Carddata
