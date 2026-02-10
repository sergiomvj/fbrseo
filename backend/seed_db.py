import json
import os
import hashlib
from sqlalchemy import create_engine, text

# Import settings directly (script runs from /app where app package is available)
from app.config import settings

def seed_database():
    print("🌱 Seeding database with existing API Keys...")
    
    # Read clients_created.json
    json_path = "clients_created.json"
    if not os.path.exists(json_path):
        # Try root path if running from scripts
        json_path = "../clients_created.json"
        
    if not os.path.exists(json_path):
        print(f"❌ Could not find clients_created.json at {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        clients = json.load(f)

    # Connect to DB
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        for client in clients:
            print(f"Processing client: {client.get('system')}...")
            
            # 1. Insert Client
            client_query = text("""
                INSERT INTO clients (id, name, company, email, is_active, max_api_keys, rate_limit_per_minute, rate_limit_per_day, created_at, updated_at)
                VALUES (:id, :name, 'FBR Apps', :email, true, 5, 120, 50000, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """)
            
            conn.execute(client_query, {
                "id": client["client_id"],
                "name": f"Sistema {client['system']}",
                "email": f"{client['system'].lower()}@fbrapps.com"
            })
            
            # 2. Insert API Key
            # We need to hash the key to store it safely (assuming backend compares hashes)
            # The previous script generated: full_key, key_hash, last_chars
            # Here we have only full_key. We must re-hash it.
            
            full_key = client["api_key"]
            key_hash = hashlib.sha256(full_key.encode()).hexdigest()
            last_chars = full_key[-4:]
            prefix = full_key.split('_')[0] + "_" + full_key.split('_')[1] # sk_live
            
            permissions = [
                "keywords:read", "keywords:write",
                "rankings:read", "rankings:write",
                "backlinks:read", "onpage:read",
                "competitors:read", "data:import"
            ]
            permissions_json = json.dumps(permissions)

            key_query = text("""
                INSERT INTO api_keys (client_id, key_prefix, key_hash, key_last_chars, name, description, status, permissions, created_at, total_requests)
                VALUES (:client_id, :prefix, :hash, :last, :name, 'Recovered from JSON', 'active', :perms, NOW(), 0)
                ON CONFLICT (key_hash) DO NOTHING
            """)
            
            conn.execute(key_query, {
                "client_id": client["client_id"],
                "prefix": prefix,
                "hash": key_hash,
                "last": last_chars,
                "name": f"Production Key - {client['system']}",
                "perms": permissions_json
            })
            
            print(f"✅ seeded {client['system']}")
            
        conn.commit()
    print("🎉 Database seeding complete!")

if __name__ == "__main__":
    seed_database()
