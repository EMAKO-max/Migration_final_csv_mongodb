import unittest
import pandas as pd
from pymongo import MongoClient
from import_csv import (
    clean_dataframe,
    migrate_to_mongodb,
    create_indexes,
    CSV_FILE,
    MONGO_URI,
    DB_NAME,
    COLLECTION_NAME
)

class TestMigrationIntegrity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Lecture et nettoyage du CSV
        df = pd.read_csv(CSV_FILE)
        df = clean_dataframe(df)
        cls.df_cleaned = df

        # Migration dans MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        cls.collection = migrate_to_mongodb(df)

        # Création des index
        create_indexes(cls.collection)

    def test_name_formatting(self):
        """Vérifie que les noms des patients sont correctement normalisés"""
        for name in self.df_cleaned["Name"].dropna():
            self.assertTrue(all(word[0].isupper() for word in name.split()))

    def test_doctor_formatting(self):
        """Vérifie que les noms des docteurs sont correctement normalisés"""
        for doc in self.df_cleaned["Doctor"].dropna():
            self.assertTrue(all(word[0].isupper() for word in doc.split()))

    def test_date_conversion(self):
        """Vérifie que les dates sont bien converties en datetime"""
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.df_cleaned["Date of Admission"]))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.df_cleaned["Discharge Date"]))

    def test_mongo_insert_count(self):
        """Vérifie que toutes les lignes du CSV sont bien migrées dans MongoDB"""
        count_in_mongo = self.collection.count_documents({})
        self.assertEqual(len(self.df_cleaned), count_in_mongo)

    def test_indexes_exist(self):
        """Vérifie que les index sont bien créés"""
        indexes = list(self.collection.index_information().keys())
        self.assertIn("Name_1", indexes)
        self.assertIn("Doctor_1", indexes)
        self.assertIn("Date of Admission_1", indexes)

    def test_columns_integrity(self):
        """Vérifie que toutes les colonnes attendues sont présentes"""
        expected_columns = [
            'Name','Age','Gender','Blood Type','Medical Condition','Date of Admission',
            'Doctor','Hospital','Insurance Provider','Billing Amount','Room Number',
            'Admission Type','Discharge Date','Medication','Test Results'
        ]
        self.assertTrue(all(col in self.df_cleaned.columns for col in expected_columns))

    def test_no_missing_values(self):
        """Vérifie qu’il n’y a pas de valeurs manquantes"""
        missing = self.df_cleaned.isnull().sum().sum()
        self.assertEqual(missing, 0)

    def test_no_exact_duplicates(self):
        """Vérifie qu’il n’y a pas de doublons exacts sur tous les champs sauf _id dans MongoDB"""
        sample_doc = self.collection.find_one()
        if sample_doc:
            fields = [k for k in sample_doc.keys() if k != "_id"]
            pipeline = [
                {"$group": {
                    "_id": {field: f"${field}" for field in fields},
                    "count": {"$sum": 1}
                }},
                {"$match": {"count": {"$gt": 1}}}
            ]
            duplicates = list(self.collection.aggregate(pipeline))
            self.assertFalse(duplicates, "Des doublons exacts ont été trouvés dans MongoDB !")

if __name__ == "__main__":
    unittest.main(verbosity=2)
