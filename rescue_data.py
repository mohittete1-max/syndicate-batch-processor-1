import os
import shutil

def rescue_target_files():
    print("=================================================================")
    print("                 SYNDICATE DATA RESCUE PROTOCOL                  ")
    print("=================================================================")
    
    TARGET_MATCHES = ["ADF_vs_ECR", "ECR_vs_ADF", "SA_vs_NAM", "SCO_W_vs_NED_W"]
    archive_dir = "Archive_GPP"
    
    for match in TARGET_MATCHES:
        archived_file = os.path.join(archive_dir, f"{match}_GPP_Jackpot.csv")
        clean_file = f"{match}.csv"
        
        if os.path.exists(archived_file):
            shutil.move(archived_file, clean_file)
            print(f"  [RESCUED] {archived_file}  -->  {clean_file}")
        else:
            print(f"  [WARNING] Could not find {archived_file} in Archive.")
            
    print("=================================================================")
    print("[RESCUE COMPLETE] Your clean target files are ready for the batch.")
    print("=================================================================")

if __name__ == "__main__":
    rescue_target_files()
