# Speedtest Monitor - Source Code Documentation

This directory contains the modular, refactored source code for the Speedtest Monitor application.

## 📁 **Module Structure**

### `config.py` - Configuration Management
- **Purpose**: Centralized configuration and constants
- **Contains**: File paths, SMB settings, CSV field definitions, exit codes
- **Benefits**: Single source of truth for all configuration values

### `logging_config.py` - Logging System
- **Purpose**: Logging setup and configuration
- **Functions**: 
  - `setup_logging()`: Initialize logging system
  - `get_logger(name)`: Get module-specific logger
- **Features**: File + console logging, debug mode support

### `speedtest_runner.py` - Speed Test Execution
- **Purpose**: Core speed test functionality
- **Functions**:
  - `run_speed_test()`: Execute complete speed test
- **Features**: Detailed error handling, comprehensive logging

### `csv_handler.py` - Data Persistence  
- **Purpose**: CSV file operations and data management
- **Functions**:
  - `save_to_csv(data)`: Save successful test results
  - `save_failure_to_csv(error_type, details, stage)`: Log failures
  - `get_csv_stats()`: Get file statistics
- **Features**: Automatic header creation, error truncation

### `smb_sync.py` - Network File Synchronization
- **Purpose**: SMB share mounting and file synchronization
- **Functions**:
  - `sync_to_smb()`: Sync local files to SMB share
  - `check_smb_mount()`: Verify SMB accessibility
  - `get_smb_status()`: Detailed mount status
  - `copy_file_with_sudo(src, dest)`: Permission-aware file copying
- **Features**: Sudo fallback, comprehensive mount checking

### `main.py` - Application Orchestration
- **Purpose**: Main application logic and coordination
- **Functions**:
  - `main()`: Primary execution function
- **Features**: Clean error handling, proper exit codes, module coordination

### `__init__.py` - Package Definition
- **Purpose**: Makes `src` a proper Python package
- **Exports**: Key functions for external use
- **Version**: 2.0.0 (modular architecture)

## 🔄 **Execution Flow**

1. **Initialization** (`main.py`)
   - Setup logging system
   - Log SMB status for diagnostics

2. **Speed Test** (`speedtest_runner.py`)
   - Execute internet speed test
   - Handle various error scenarios
   - Return structured results

3. **Data Persistence** (`csv_handler.py`)
   - Save results to local CSV file
   - Log failures if speed test failed

4. **Network Sync** (`smb_sync.py`)
   - Sync data to SMB share
   - Handle permission and mount issues

5. **Cleanup** (`main.py`)
   - Log completion status
   - Return appropriate exit code

## 🎯 **Benefits of Modular Architecture**

### **Maintainability**
- Each module has single responsibility
- Easy to locate and fix issues
- Clear separation of concerns

### **Testability**
- Individual modules can be tested in isolation
- Mock dependencies easily for unit tests
- Clearer test scenarios

### **Reusability**
- Modules can be imported and used independently
- Functions available for other scripts
- Clean API boundaries

### **Readability**
- Smaller, focused files
- Clear module purposes
- Better code organization

### **Extensibility**
- Easy to add new features
- Simple to modify existing functionality
- Plugin-like architecture possible

## 🚀 **Usage Examples**

### Import Individual Functions
```python
from src.speedtest_runner import run_speed_test
from src.csv_handler import save_to_csv
from src.smb_sync import get_smb_status

# Run just a speed test
result = run_speed_test()

# Check SMB status
status = get_smb_status()
```

### Use as Package
```python
import src

# Run complete application
exit_code = src.main()

# Or use individual components
logger = src.setup_logging()
csv_stats = src.get_csv_stats()
```

## 🔧 **Development Guidelines**

### **Adding New Features**
1. Determine appropriate module (or create new one)
2. Follow existing error handling patterns
3. Use the centralized logger
4. Update `__init__.py` exports if needed

### **Configuration Changes**
- All constants should go in `config.py`
- Use Path objects for file paths
- Follow existing naming conventions

### **Error Handling**
- Use module-specific loggers
- Follow existing exception patterns
- Always log failures to CSV when appropriate

## 📊 **File Size Reduction**

**Before**: `speedtest_monitor.py` - 435 lines (monolithic)
**After**: 
- `main.py` - ~80 lines
- `speedtest_runner.py` - ~120 lines  
- `csv_handler.py` - ~80 lines
- `smb_sync.py` - ~150 lines
- `config.py` - ~30 lines
- `logging_config.py` - ~40 lines

**Total**: ~500 lines across 6 focused modules vs 435 lines in 1 file
**Result**: Better organization with minimal overhead