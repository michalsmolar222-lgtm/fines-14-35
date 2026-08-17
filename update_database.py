import os
import subprocess
import glob

def run_script(script_name):
    print(f"\n[{'='*40}]")
    print(f"🔄 Spúšťam: {script_name}")
    print(f"[{'='*40}]\n")
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Chyba pri spúšťaní {script_name}: {e}")
    except FileNotFoundError:
        print(f"❌ Skript {script_name} sa nenašiel!")

def main():
    print("🚀 Začínam aktualizáciu všetkých databáz (cenníkov)...\n")
    
    scripts = [
        "generate_all.py",
        "generate_beds.py",
        "generate_beds_v2.py",
        "generate_chairs.py",
        "generate_doplnky.py",
        "generate_jednolozka.py",
        "generate_masiv.py",
        "generate_pohovky.py",
        "generate_postele_sirky.py",
        "generate_rosty.py"
    ]
    
    # Check what scripts actually exist
    existing_scripts = []
    for script in scripts:
        if os.path.exists(script):
            existing_scripts.append(script)
        else:
            print(f"⚠️ Skript {script} sa nenašiel na disku. Bude preskočený.")
            
    # Run them sequentially
    for script in existing_scripts:
        run_script(script)
        
    print("\n✅ Aktualizácia databáz bola dokončená!")

if __name__ == "__main__":
    main()
