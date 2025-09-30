# update_executor.py

import sys
from pathlib import Path
import os
import shutil


from processing import find_new_bundle_path, process_mod_update

def console_log(message: str):
    """
    A simple logging function.
    """
    print(message)

def update_mod_function(old_mod_path_str: str, game_resource_dir_str: str, working_dir_str: str = "./updated_mods") -> tuple[bool, str, Path | None]:
    """
    Automates the Mod update process using paths passed directly as strings.

    Args:
        old_mod_path_str: Full path (string) to the old, modified bundle file.
        game_resource_dir_str: Full path (string) to the folder containing the new game bundles.
        working_dir_str: The folder where the final updated file will be saved.

    Returns:
        A tuple: (success: bool, message: str, final_file_path: Path | None)
    """
    # --- 1. Path Setup and Validation ---
    old_mod_path = Path(old_mod_path_str)
    game_resource_dir = Path(game_resource_dir_str)
    working_dir = Path(working_dir_str)
    
    # We will only replace Texture2D by default
    asset_types_to_replace = {"Texture2D", "TextAsset"}
    
    if not old_mod_path.is_file():
        return False, f"Error: Old Mod file not found: {old_mod_path}", None
    if not game_resource_dir.is_dir():
        return False, f"Error: Game resource folder not found: {game_resource_dir}", None

    working_dir.mkdir(exist_ok=True)
    
    console_log(f"\n--- Mod Update Initiated ---")
    
    # --- 2. Find the New Bundle ---
    console_log("\n[Step 1/3] Searching for the matching new game bundle...")
    new_bundle_path, find_msg = find_new_bundle_path(old_mod_path, game_resource_dir, console_log)
    
    if not new_bundle_path:
        return False, f"New file search failed: {find_msg}", None
        
    console_log(f"\n✅ Found new game file: {new_bundle_path.name}")
    
    # --- 3. Run the Update Process ---
    console_log("\n[Step 2/3] Performing Bundle-to-Bundle resource replacement...")
    
    # Assuming CRC correction is necessary (perform_crc=True) and padding is enabled
    success, result_msg = process_mod_update(
        old_mod_path=old_mod_path,
        new_bundle_path=new_bundle_path,
        working_dir=working_dir,
        enable_padding=True,
        log=console_log,
        perform_crc=True,
        asset_types_to_replace=asset_types_to_replace
    )
    
    # --- 4. Final Output ---
    final_path = working_dir / new_bundle_path.name if success else None
    
    if success:
        console_log("\n--- Mod Update Finished ---")
        return True, f"SUCCESS: Update completed. {result_msg}", final_path
    else:
        return False, f"FAILURE: Update failed. {result_msg}", None

# Example of how you would call this function from your main program:
def updateMod(OLD_MOD, GAME_RESOURCES, OUTPUT_FOLDER):

    # --- CALL THE FUNCTION ---
    status, message, result_path = update_mod_function(
        old_mod_path_str=OLD_MOD,
        game_resource_dir_str=GAME_RESOURCES,
        working_dir_str=OUTPUT_FOLDER
    )
    
    return status,message,result_path 