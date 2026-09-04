import os
import glob
import shutil

def sanitize_workspace():
    print("=================================================================")
    print("           SYNDICATE WORKSPACE SANITIZATION PROTOCOL             ")
    print("=================================================================")
    
    archive_dir = "Archive_GPP"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"[SYSTEM] Created archive directory: {archive_dir}")

    all_csvs = glob.glob("*.csv")
    
    # Keywords that flag a file as old Phase 2/GPP experimental data
    archive_keywords = [
        "gpp", "jackpot", "sleep_safe", "optimal", "master", 
        "aggression", "portfolio", "audited", "rank1", "export"
    ]

    archived_count = 0
    renamed_count = 0

    for file in all_csvs:
        # Protect system outputs and active staging files
        if "H2H_Cash" in file or "match_squad_data" in file:
            continue

        lower_name = file.lower()
        
        # 1. Archive the old experiments
        if any(keyword in lower_name for keyword in archive_keywords):
            shutil.move(file, os.path.join(archive_dir, file))
            print(f"  [ARCHIVED] Moved -> {file}")
            archived_count += 1
            
        # 2. Fix the raw file formatting (replace spaces with underscores)
        else:
            if " " in file:
                new_name = file.replace(" ", "_")
                os.rename(file, new_name)
                print(f"  [RENAMED] Raw file -> {new_name}")
                renamed_count += 1

    print("=================================================================")
    print(f"[CLEANUP COMPLETE] Archived {archived_count} files | Renamed {renamed_count} files")
    print("=================================================================")

if __name__ == "__main__":
    sanitize_workspace()
