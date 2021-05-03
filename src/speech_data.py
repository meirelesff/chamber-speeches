from pymongo import MongoClient
from io import BytesIO
import pandas as pd
import requests
import os


class DiscursosCamara:
    '''
    Tools to extract Brazilian federal deputies' floor speeches

        Methods include:
            - Extraction of the list of deputies;
            - Creation of a mongodb collection to store data;
            - A client to retrieve data from the Brazilian Chamber of Deputies'
            API.

        Params:
            - start_legis: First legislature (defaults to 48);
            - mongo_add: mongodb address (defaults to 'localhost')
            - dbname: a name for mongo db
            - collname: name of the collection to store speench data
            - start_legis: ID of initial legislature
    '''
    def __init__(self, mongo_add, dbname, collname, start_legis):
        self.start_legis = int(start_legis)
        self.mongo_host = mongo_add
        self.dbname = dbname
        self.collname = collname
        self.s = requests.Session()

    def cria_collection(self):
        # Connect to mongo, create db and collections
        self.cl = MongoClient(host=self.mongo_host)
        self.db = self.cl[self.dbname]
        self.coll = self.db[self.collname]

    def drop_collection(self):
        self.coll.drop()

    def lista_deps_camara(self):
        # Extract deputies' ids from the chambers' website
        url = "https://dadosabertos.camara.leg.br/arquivos/deputados/csv/deputados.csv"
        deps = pd.read_csv(url, sep=";")
        deps = deps.loc[(deps.idLegislaturaInicial >= self.start_legis) | (deps.idLegislaturaFinal >= self.start_legis)]
        deps = deps[["uri", "nome", "siglaSexo"]]
        deps.loc[:, "uri"] = deps.loc[:, "uri"].apply(lambda x: x.split("/")[6])
        self.deps = deps

    def parse_json(self, json_cam, uri):
        # Add deputies uri and remove escape chars from speech data
        json_cam["uri"] = uri
        json_cam["transcricao"] = json_cam["transcricao"].replace("\r\n", " ")
        return json_cam

    def discursos_dep(self, uri):

        # Initial endpoint
        print("Discurdos do ID: " + str(uri))
        endpoint = "https://dadosabertos.camara.leg.br/api/v2/deputados/{uri}/discursos?dataInicio=2001-01-01&dataFim=2021-01-01&ordenarPor=dataHoraInicio&ordem=ASC&itens=100&pagina=1"
        endpoint = endpoint.format(uri = uri)
        manter=True

        # Loop over item pages
        while manter:
        
            try:
                req = self.s.get(endpoint, timeout=5)
            except:
                print("Erro na requisição do ID " + uri)
                return None
    
            if not req.ok:
                print("Erro na requisição do ID " + uri)
                return None

            if not req.json()["dados"]:
                return None

            # Parse json and add deputy ids in the documents
            req = req.json()
            spch = [self.parse_json(x, uri) for x in req["dados"]]

            # Send data to collection
            up = self.coll.insert_many(spch)

            # Pagination
            atual = req["links"][0]["href"]
            proxima = req["links"][2]["href"]

            if atual == proxima:
                manter=False
            else:
                endpoint=proxima

    def extrai_discursos(self):
        # Start new collection
        self.cria_collection()
        
        # Extract deputies' list
        self.lista_deps_camara()   

        # Extract speech data 
        for i in self.deps.uri:
            self.discursos_dep(i)

        self.cl.close()



if __name__ == "__main__":
    cam = DiscursosCamara(mongo_add=os.environ["MONGOADD"], 
                          dbname=os.environ["DBNAME"], 
                          collname=os.environ["COLLNAME"],
                          start_legis=os.environ["START_LEGIS"])
    cam.extrai_discursos()

