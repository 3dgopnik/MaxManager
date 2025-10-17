# MaxINI Editor Presets

This directory contains preset configurations for the MaxINI Editor.

## Built-in Presets

The following presets are built into the MaxINI Editor:

### Performance Presets
- **High Performance** - Optimized for maximum rendering performance
- **Memory Optimized** - Optimized for large scenes with high memory usage

### Renderer Presets
- **Arnold Renderer** - Optimized for Arnold rendering workflow
- **V-Ray Renderer** - Optimized for V-Ray rendering workflow

### General Presets
- **Minimal** - Minimal settings for basic 3ds Max functionality

## User Presets

You can create your own presets by adding JSON files to this directory.

### Preset Format

```json
{
  "name": "Preset Name",
  "description_en": "English description",
  "description_ru": "Russian description",
  "author": "Your Name",
  "parameters": {
    "RenderThreads": 8,
    "UseAllCores": true,
    "ThreadPriority": 2,
    "MemoryPool": 2048,
    "DynamicHeapSize": true,
    "PageFileSize": 8192,
    "ViewportPerformanceMode": 1,
    "AutoBackup": true,
    "BackupInterval": 10
  },
  "tags": ["performance", "custom"],
  "version": "1.0",
  "created_date": "2025-10-17",
  "category": "Custom"
}
```

### Parameter Reference

| Parameter | Type | Description | Range |
|-----------|------|-------------|-------|
| `RenderThreads` | Integer | Number of rendering threads | 1-32 |
| `UseAllCores` | Boolean | Use all available CPU cores | true/false |
| `ThreadPriority` | Integer | Thread priority level | 0-4 |
| `MemoryPool` | Integer | Memory pool size (MB) | 256-8192 |
| `DynamicHeapSize` | Boolean | Enable dynamic heap sizing | true/false |
| `PageFileSize` | Integer | Page file size (MB) | 1024-32768 |
| `ViewportPerformanceMode` | Integer | Viewport performance mode | 0-2 |
| `AutoBackup` | Boolean | Enable automatic backups | true/false |
| `BackupInterval` | Integer | Backup interval (minutes) | 5-60 |

### Categories

- **Performance** - Performance optimization presets
- **Memory** - Memory management presets
- **Renderers** - Renderer-specific presets
- **General** - General purpose presets
- **User** - User-created custom presets

## Installation

1. Place your `.json` preset files in this directory
2. Restart the MaxINI Editor
3. Your presets will appear in the "Load Preset..." dialog

## Examples

See `example_user_preset.json` for a complete example of a user preset.
