"""
Script to improve parameter display names in ini_parameters_database.json.

Converts:
- "Autobackup.AutoBackupInterval" -> "Auto Backup Interval"
- "MAXScript.LoadStartupScripts" -> "Load Startup Scripts"
- Makes names more human-readable by splitting CamelCase and removing section prefix
"""

import json
import re
from pathlib import Path


def split_camel_case(text: str) -> str:
    """Split CamelCase text into separate words."""
    # Add space before uppercase letters
    result = re.sub(r'([A-Z])', r' \1', text)
    # Clean up multiple spaces
    result = ' '.join(result.split())
    return result.strip()


def improve_display_name(key: str, current_name: str, language: str) -> str:
    """
    Improve display name to be more human-readable.
    
    Args:
        key: Parameter key (e.g., "Autobackup.AutoBackupInterval")
        current_name: Current display name
        language: "en" or "ru"
    
    Returns:
        Improved display name
    """
    # If current name is just the key, improve it
    if current_name == key or not current_name:
        # Remove section prefix (before last dot)
        if '.' in key:
            param_name = key.split('.')[-1]
        else:
            param_name = key
        
        # Split CamelCase
        human_name = split_camel_case(param_name)
        
        # For Russian, keep English technical terms but could translate common words
        if language == "ru":
            # Keep the English name for now, translation can be done manually later
            # This ensures we don't lose information
            return human_name
        
        return human_name
    
    # If name already looks good, keep it
    return current_name


def process_database(input_path: Path, output_path: Path = None):
    """Process the database and improve all display names."""
    print(f"Loading database from: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Skip metadata
    metadata = data.pop('_metadata', None)
    
    improved_count = 0
    total_params = len(data)
    
    print(f"Processing {total_params} parameters...")
    
    for key, param_data in data.items():
        # Process English display name
        if 'en' in param_data and 'display_name' in param_data['en']:
            old_name = param_data['en']['display_name']
            new_name = improve_display_name(key, old_name, 'en')
            if new_name != old_name:
                param_data['en']['display_name'] = new_name
                improved_count += 1
                print(f"  [EN] {key}: '{old_name}' -> '{new_name}'")
        
        # Process Russian display name
        if 'ru' in param_data and 'display_name' in param_data['ru']:
            old_name = param_data['ru']['display_name']
            new_name = improve_display_name(key, old_name, 'ru')
            if new_name != old_name:
                param_data['ru']['display_name'] = new_name
                improved_count += 1
                print(f"  [RU] {key}: '{old_name}' -> '{new_name}'")
    
    # Add metadata back
    if metadata:
        metadata['improvements_v2'].append("Improved display names to be more human-readable (split CamelCase)")
        data = {'_metadata': metadata, **data}
    
    # Save to output
    output_path = output_path or input_path
    print(f"\nSaving improved database to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Done! Improved {improved_count} display names out of {total_params * 2} total (EN + RU)")


if __name__ == "__main__":
    # Paths
    repo_root = Path(__file__).parent.parent
    input_json = repo_root / "docs" / "ini_parameters_database.json"
    
    # Create backup first
    backup_path = input_json.parent / "ini_parameters_database_backup.json"
    print(f"Creating backup: {backup_path}")
    
    import shutil
    shutil.copy2(input_json, backup_path)
    
    # Process
    process_database(input_json)
    
    print("\n🎉 All done! Check the results.")

