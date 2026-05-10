"""
Migrate users to new backend by calling the signup API endpoint

Usage:
    python migrate_users_via_api.py --dry-run          # Preview only
    python migrate_users_via_api.py                    # Actual migration
"""

import csv
import requests
import json
import time
import sys

# Configuration
API_BASE_URL = "http://18.207.46.68/api/v1"
SIGNUP_ENDPOINT = f"{API_BASE_URL}/user/signup/parent/"
CSV_FILE = "users_export.csv"

def migrate_users(dry_run=False):
    print("\n" + "="*60)
    print("=== Migrating Users to New Backend via API ===")
    print("="*60 + "\n")
    
    # Read CSV file
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            users = list(reader)
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found: {CSV_FILE}")
        print("\nFirst, create the CSV file:")
        print("  sqlite3 old_db.sqlite3 << 'EOF'")
        print("  .mode csv")
        print("  .output users_export.csv")
        print("  SELECT first_name, last_name, email FROM users WHERE deleted_at IS NULL;")
        print("  .quit")
        print("  EOF")
        return
    
    total = len(users)
    print(f"📊 Found {total} users in CSV file\n")
    print(f"🔗 API Endpoint: {SIGNUP_ENDPOINT}")
    print(f"🔄 Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE MIGRATION'}\n")
    
    migrated = 0
    failed = 0
    skipped = 0
    errors = []
    
    for idx, row in enumerate(users, 1):
        # Parse CSV row
        if len(row) < 3:
            skipped += 1
            continue
        
        first_name = row[0].strip()
        last_name = row[1].strip()
        email = row[2].strip().lower()
        
        if not email or not first_name:
            skipped += 1
            continue
        
        full_name = f"{first_name} {last_name}".strip()
        
        # Prepare payload (same as your Postman example)
        payload = {
            "email": email,
            "full_name": full_name,
            "date_of_birth": "2000-01-01",  # Default placeholder
            "password": "user@1234",
            "password_confirm": "user@1234"
        }
        
        # Display progress
        progress = f"[{idx}/{total}]"
        status_msg = f"{progress} Creating user: {email}... "
        print(status_msg, end="", flush=True)
        
        if dry_run:
            print("✓ [DRY RUN]")
            migrated += 1
            continue
        
        # Make API request
        try:
            response = requests.post(
                SIGNUP_ENDPOINT,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                print("✓")
                migrated += 1
            elif response.status_code == 400:
                # Likely validation error or already exists
                try:
                    error_data = response.json()
                    error_msg = str(error_data).get('detail', 'Validation error')[:50]
                except:
                    error_msg = "Email might already exist"
                
                print(f"⊘ ({error_msg})")
                skipped += 1
            else:
                error_text = response.text[:100] if response.text else "No response"
                print(f"✗ (HTTP {response.status_code})")
                errors.append(f"{email}: {error_text}")
                failed += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.2)
        
        except requests.exceptions.Timeout:
            print("✗ (Timeout)")
            errors.append(f"{email}: Request timeout")
            failed += 1
        except requests.exceptions.ConnectionError:
            print("✗ (Connection error)")
            print(f"\n❌ Cannot connect to API at {SIGNUP_ENDPOINT}")
            print("   Make sure the backend is running at http://18.207.46.68")
            return
        except Exception as e:
            print(f"✗ ({str(e)[:40]})")
            errors.append(f"{email}: {str(e)[:50]}")
            failed += 1
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ Migrated: {migrated}")
    print(f"⊘ Skipped:  {skipped}")
    print(f"✗ Failed:   {failed}")
    print("="*60 + "\n")
    
    if dry_run:
        print("🔍 [DRY RUN MODE] No changes were made.")
        print("   Run without --dry-run to perform actual migration.\n")
    elif failed > 0:
        print("⚠️  Some users failed. Errors:\n")
        for error in errors[:5]:
            print(f"   • {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")
        print()
    else:
        print("✅ Migration completed successfully!\n")

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    migrate_users(dry_run=dry_run)
