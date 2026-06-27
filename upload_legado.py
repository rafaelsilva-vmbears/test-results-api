import pymongo
import os
import glob
import httpx

# 1. Clear Database
print("Conectando ao MongoDB para limpar banco...")
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test_results"]
db.runs.drop()
db.projects.drop()
print("Banco de dados 'test_results' limpo com sucesso!")

# 2. Upload files
API_KEY = "j7NgyCnqEn3a3kzkm5aklSyi36EiwOCC"
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("API_KEY="):
                API_KEY = line.strip().split("=")[1].strip('"').strip("'")
                break

files = glob.glob("legado/*.xml")
if not files:
    print("Nenhum arquivo XML encontrado em legado/")
else:
    print(f"Iniciando upload de {len(files)} arquivos XML...")
    for filepath in files:
        with open(filepath, "rb") as f:
            print(f"-> Fazendo upload de {os.path.basename(filepath)}...")
            files_dict = {'file': (os.path.basename(filepath), f, 'application/xml')}
            response = httpx.post(
                "http://localhost:8000/xml-execution/process-and-save?project=teste&environment=rc&source=xml",
                headers={"X-API-Key": API_KEY},
                files=files_dict,
                timeout=30.0
            )
            if response.status_code == 201:
                print("   [OK]", response.json())
            else:
                print("   [ERRO]", response.status_code, response.text)
