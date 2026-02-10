import json
import os
import hashlib
from sqlalchemy import create_engine, text

# Import settings directly (script runs from /app where app package is available)
from app.config import settings

def seed_database():
    print("🌱 Seeding database with existing API Keys...")
    
    # Pre-defined keys (using Env Vars for security)
    # The keys will be loaded from environment variables in your deployment settings (Easypanel/VPS)
    keys_to_seed = [
        {"system": "Planner", "client_id": 3, "api_key": os.getenv("PLANNER_API_KEY")},
        {"system": "Blogger", "client_id": 4, "api_key": os.getenv("BLOGGER_API_KEY")},
        {"system": "Creator", "client_id": 5, "api_key": os.getenv("CREATOR_API_KEY")},
        {"system": "VideoCreator", "client_id": 6, "api_key": os.getenv("VIDEOCREATOR_API_KEY")},
        {"system": "TVFACEBRASIL", "client_id": 8, "api_key": os.getenv("TVFACEBRASIL_API_KEY")},
    ]
    
    # Also look for the TVFACEBRASIL key specifically from a known "safe" place if not in env
    if not os.getenv("TVFACEBRASIL_API_KEY"):
        # The key provided by user is sensitive and should be set as an environment variable (sk_live_...)
        # Github blocks this specific format. We must use an Env Var.
        pass
    
    # Try to read additional keys from JSON if it exists
    json_path = "api_keys_generated.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                extra_keys = json.load(f)
                # Merge or append
                for ek in extra_keys:
                    if not any(k['api_key'] == ek['api_key'] for k in keys_to_seed):
                        keys_to_seed.append(ek)
        except Exception as e:
            print(f"⚠️ Could not read {json_path}: {e}")

    # Connect to DB
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        for client in keys_to_seed:
            print(f"Processing client: {client.get('system')}...")
            
            system_name = client.get('system', 'Unknown')
            client_id = client.get('client_id')
            full_key = client.get('api_key')
            
            if not full_key:
                print(f"⏩ Skipping {system_name} (no key)")
                continue

            # 1. Insert Client
            client_query = text("""
                INSERT INTO clients (id, name, company, email, is_active, max_api_keys, rate_limit_per_minute, rate_limit_per_day, created_at, updated_at)
                VALUES (:id, :name, 'FBR Apps', :email, true, 5, 120, 50000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email
            """)
            
            conn.execute(client_query, {
                "id": client_id,
                "name": f"Sistema {system_name}",
                "email": f"{system_name.lower()}@fbrapps.com"
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
                VALUES (:client_id, :prefix, :hash, :last, :name, 'Recovered from JSON/Hardcoded', 'active', :perms, CURRENT_TIMESTAMP, 0)
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
