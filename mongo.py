from pymongo import MongoClient

client = MongoClient("mongodb+srv://saksha914:1234@cluster0.2c6vo.mongodb.net/fund_tracker?retryWrites=true&w=majority&appName=Cluster0")
db = client["fund-tracker"]  # Replace with your actual database name
db.create_collection("summarizer_projectpdf")  # Ensure collection name matches your model

print("Collection created successfully!")
