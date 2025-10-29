#!/usr/bin/env python3
"""
Validation daemon with state management
Supports: start, pause, resume, stop
"""
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')
from auto_validator import ParameterValidator

class ValidatorDaemon:
    """Validator with state management and controls"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.state_file = Path(__file__).parent / 'validation_state.json'
        self.progress_file = Path(__file__).parent / 'progress.json'
        self.log_file = Path(__file__).parent / 'validation_log.jsonl'
        
        self.load_state()
        self.validator = ParameterValidator()
    
    def load_state(self):
        """Load validation state"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        else:
            self.state = {
                'validated_params': [],
                'last_index': 0,
                'total': 0,
                'status': 'idle',
                'started_at': None,
                'paused_at': None
            }
    
    def save_state(self):
        """Save validation state"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)
    
    def update_progress(self, validated: int, current: str, total: int):
        """Update progress for dashboard"""
        progress = {
            'total': total,
            'validated': validated,
            'current': current,
            'status': self.state['status'],
            'percent': round(validated / total * 100, 1) if total > 0 else 0
        }
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f)
    
    def check_control(self) -> str:
        """Check for control signals"""
        if not self.state_file.exists():
            return 'stop'
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        return state.get('status', 'idle')
    
    def run(self):
        """Run validation with state management"""
        print("=" * 80)
        print("VALIDATOR DAEMON - Starting")
        print("=" * 80)
        
        # Load database
        with open(self.db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        params = {k: v for k, v in db.items() if k != '_metadata'}
        param_list = list(params.items())
        
        self.state['total'] = len(param_list)
        self.state['status'] = 'running'
        self.state['started_at'] = datetime.now().isoformat()
        self.save_state()
        
        # Resume from last position
        start_idx = self.state['last_index']
        validated_set = set(self.state['validated_params'])
        
        print(f"Resuming from index {start_idx}/{len(param_list)}")
        print(f"Already validated: {len(validated_set)} parameters")
        print("=" * 80)
        
        for idx in range(start_idx, len(param_list)):
            param_name, param_data = param_list[idx]
            
            # Check control signal
            control = self.check_control()
            if control == 'paused':
                print("\n[PAUSED] Validation paused by user")
                self.state['paused_at'] = datetime.now().isoformat()
                self.save_state()
                return
            elif control == 'stop':
                print("\n[STOPPED] Validation stopped by user")
                self.state['status'] = 'stopped'
                self.save_state()
                return
            
            # Skip if already validated
            if param_name in validated_set:
                continue
            
            # Update progress
            self.update_progress(len(validated_set), param_name, len(param_list))
            
            # Validate
            print(f"\n[{idx+1}/{len(param_list)}] {param_name}")
            validation = self.validator.validate_parameter(param_name, param_data)
            
            # Update parameter
            if validation['status_verified']:
                param_data['status'] = validation['status']
            
            if validation['community_notes']:
                param_data['community_notes'] = validation['community_notes']
            
            if validation['warnings']:
                if 'warnings' not in param_data:
                    param_data['warnings'] = {}
                param_data['warnings']['en'] = ' | '.join(validation['warnings'])
            
            param_data['last_verified'] = validation['last_verified']
            
            # Mark as PHANTOM if not found anywhere
            if not validation['status_verified'] and not validation['community_notes']:
                param_data['phantom'] = True
                param_data['phantom_note'] = 'Not found in any source - may be AI hallucination or very rare parameter'
                print(f"  ⚠️ PHANTOM detected!")
            
            # Log
            log_entry = {
                'timestamp': validation['last_verified'],
                'parameter': param_name,
                'status': validation['status'],
                'verified': validation['status_verified'],
                'phantom': param_data.get('phantom', False),
                'notes_count': len(validation['community_notes']),
                'warnings_count': len(validation['warnings']),
                'community_notes': validation['community_notes'],
                'warnings': validation['warnings']
            }
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            # Update state
            validated_set.add(param_name)
            self.state['validated_params'] = list(validated_set)
            self.state['last_index'] = idx + 1
            self.save_state()
            
            # Save database periodically (every 10 params)
            if len(validated_set) % 10 == 0:
                db_updated = {'_metadata': db['_metadata'], **dict(sorted(params.items()))}
                with open(self.db_path, 'w', encoding='utf-8') as f:
                    json.dump(db_updated, f, indent=2, ensure_ascii=False)
                print(f"  💾 Database saved (checkpoint)")
        
        # Final save
        db_updated = {'_metadata': db['_metadata'], **dict(sorted(params.items()))}
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(db_updated, f, indent=2, ensure_ascii=False)
        
        self.state['status'] = 'completed'
        self.save_state()
        
        print("\n" + "=" * 80)
        print(f"VALIDATION COMPLETE")
        print(f"Validated: {len(validated_set)}/{len(param_list)}")
        
        # Count phantoms
        phantoms = [k for k, v in params.items() if v.get('phantom')]
        print(f"Phantoms found: {len(phantoms)}")
        
        print("=" * 80)

if __name__ == '__main__':
    db_path = Path(__file__).parent.parent / 'docs' / 'maxini_ultimate_master_v2.json'
    daemon = ValidatorDaemon(str(db_path))
    daemon.run()

