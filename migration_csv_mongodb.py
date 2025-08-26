import os
import pandas as pd
from pymongo import MongoClient

# =============================
# CONFIGURATION
# =============================
CSV_FILE = "dhealthcare_dataset.csv"

# Utilisation des variables d'environnement pour Docker
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER", "migrateUser")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "MigratePass123!")
DB_NAME = os.getenv("MONGO_DB", "Medical_db")

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource={DB_NAME}"

# Connexion MongoDB avec authentification
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
COLLECTION_NAME = "Patients"

# =============================
# ETAPE 1 - Nettoyage
# =============================
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates().copy()

    def normalize_name(name: str):
        if pd.isna(name):
            return name
        return " ".join([w.capitalize() for w in str(name).split()])

    if "Name" in df.columns:
        df["Name"] = df["Name"].apply(normalize_name)
    if "Doctor" in df.columns:
        df["Doctor"] = df["Doctor"].apply(normalize_name)

    for col in ["Date of Admission", "Discharge Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

# =============================
# ETAPE 2 - Vérification intégrité avant migration
# =============================
def check_integrity_before(df: pd.DataFrame):
    print("=== Intégrité avant migration ===")
    print("Colonnes disponibles :", df.columns.tolist())
    print("Nombre de doublons :", df.duplicated().sum())
    print("Valeurs manquantes par colonne :\n", df.isnull().sum())

# =============================
# ETAPE 3 - Migration MongoDB
# =============================
def migrate_to_mongodb(df: pd.DataFrame):
    collection = db[COLLECTION_NAME]

    collection.drop()  # Supprime l'ancienne collection
    records = df.to_dict(orient="records")
    collection.insert_many(records)
    return collection

# =============================
# ETAPE 4 - Vérification intégrité après migration
# =============================
def check_integrity_after(collection, expected_columns=None, expected_types=None):
    print("=== Intégrité après migration ===")
    count_documents = collection.count_documents({})
    print("Nombre de documents dans MongoDB :", count_documents)

    sample_doc = collection.find_one()
    if sample_doc:
        fields = [k for k in sample_doc.keys() if k != "_id"]
        pipeline = [
            {"$group": {
                "_id": {field: f"${field}" for field in fields},
                "count": {"$sum": 1}
            }},
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(collection.aggregate(pipeline))
        if duplicates:
            print(f"Doublons exacts détectés : {len(duplicates)}")
            for dup in duplicates:
                print(dup)
        else:
            print("Aucun doublon exact détecté")

        missing_counts = {k: collection.count_documents({k: None}) for k in fields}
        print("Valeurs manquantes par champ :", missing_counts)

        if expected_columns:
            missing_columns = [col for col in expected_columns if col not in sample_doc]
            if missing_columns:
                print("Colonnes manquantes :", missing_columns)
            else:
                print("Toutes les colonnes attendues sont présentes")

        if expected_types:
            for col, dtype in expected_types.items():
                value = next((doc[col] for doc in collection.find({col: {"$ne": None}})), None)
                if value is not None and not isinstance(value, dtype):
                    print(f"Type incorrect pour {col} : attendu {dtype}, trouvé {type(value)}")
                else:
                    print(f"Type correct pour {col}")

# =============================
# ETAPE 5 - Index
# =============================
def create_indexes(collection):
    collection.create_index("Name")
    collection.create_index("Doctor")
    collection.create_index("Date of Admission")
    print(" Index créés sur Name, Doctor, Date of Admission")

# =============================
# ETAPE 6 - CRUD
# =============================
def create_patient(collection, patient_data: dict):
    return collection.insert_one(patient_data).inserted_id

def read_patients(collection, query: dict = {}):
    return list(collection.find(query))

def update_patient(collection, query: dict, new_values: dict):
    return collection.update_one(query, {"$set": new_values})

def delete_patient(collection, query: dict):
    return collection.delete_one(query)

# =============================
# ETAPE 7 - Export MongoDB
# =============================
def export_from_mongodb(file_path: str):
    df = pd.DataFrame(list(db[COLLECTION_NAME].find({}, {"_id": 0})))
    df.to_csv(file_path, index=False)
    print(f"Données exportées dans {file_path}")

# =============================
# MAIN
# =============================
if __name__ == "__main__":
    df = pd.read_csv(CSV_FILE)
    df = clean_dataframe(df)

    check_integrity_before(df)

    collection = migrate_to_mongodb(df)

    check_integrity_after(collection)

    create_indexes(collection)

    export_from_mongodb("export_patients.csv")

    print("Migration terminée et données disponibles dans MongoDB.")