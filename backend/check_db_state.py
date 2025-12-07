
import sys
import os
# Backend klasörünü path'e ekle
sys.path.append(os.getcwd())

from database import SessionLocal
from models import User, Resource

def check_db():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f" - User: {u.email} (ID: {u.user_id})")
            
        resources = db.query(Resource).all()
        print(f"Total Resources: {len(resources)}")
        for r in resources:
            print(f" - Resource: {r.name} (ID: {r.resource_id}) | Active: {r.is_active} | Owner: {r.owner_id} | Type: {r.type}")
            
    except Exception as e:
        print(f"Error querying DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
