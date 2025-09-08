# Implementation Plan

[Overview]
Replace the Tkinter-based GUI with PyQt6 while preserving all existing functionality and maintaining the same user experience.

This implementation plan focuses on migrating the GUI layer from Tkinter to PyQt6, adapting the controller layer to use PyQt's signal-slot mechanism instead of callbacks, and ensuring all other modules remain unchanged. The goal is to provide a modern interface while maintaining 100% functional parity with the existing application.

[Types]
Define PyQt6 signal types and interface adaptations for the new GUI architecture.

**Signal Types:**
- `conversion_started: pyqtSignal(str, str)` - Emits token and document_id when conversion begins
- `preview_requested: pyqtSignal()` - Triggered when user wants to preview results
- `settings_requested: pyqtSignal()` - Triggered when user opens settings
- `progress_updated: pyqtSignal(float, str)` - Updates progress bar and status message
- `conversion_complete: pyqtSignal(bool, str)` - Signals conversion completion with success flag and message
- `status_logged: pyqtSignal(str, str)` - Logs status messages with level (info, success, warning, error)

**Interface Adaptations:**
- `MainWindow` class inherits from `QMainWindow` instead of being Tkinter-based
- `PreviewWindow` class inherits from `QDialog` instead of being Tkinter-based
- `SettingsWindow` class inherits from `QDialog` instead of being Tkinter-based
- All callback-based interfaces replaced with signal-slot connections

[Files]
Modify GUI layer files and adapt controller layer while preserving all other modules.

**Files to be Completely Rewritten:**
- `src/gui/main_window.py` - Replace Tkinter implementation with PyQt6 QMainWindow
- `src/gui/preview_window.py` - Replace Tkinter implementation with PyQt6 QDialog
- `src/gui/__init__.py` - Update imports and potentially add PyQt6-related exports

**Files to be Modified:**
- `src/app_controller.py` - Adapt callback mechanism to PyQt6 signal-slot system
- `main.py` - Update imports from tkinter to PyQt6 and adjust application initialization

**Files to Remain Unchanged:**
- `src/api/feishu_client.py` - All API interaction logic preserved
- `src/converter/markdown_converter.py` - All conversion logic preserved
- `src/utils/file_manager.py` - All file management logic preserved
- `src/api/__init__.py` - No changes needed
- `src/converter/__init__.py` - No changes needed
- `src/utils/__init__.py` - No changes needed
- `pyproject.toml` - Already contains PyQt6 dependency

[Functions]
Replace Tkinter-based functions with PyQt6 equivalents while maintaining identical functionality.

**New Functions in MainWindow:**
- `__init__(self)` - Initialize QMainWindow with Qt components
- `init_ui(self)` - Set up PyQt6 interface elements (replaces create_widgets)
- `setup_connections(self)` - Connect PyQt6 signals and slots
- `emit_conversion_started(self)` - Emit conversion signal instead of calling callback
- `emit_preview_requested(self)` - Emit preview signal instead of calling callback
- `emit_settings_requested(self)` - Emit settings signal instead of calling callback
- `update_progress_slot(self, value: float, message: str)` - Slot for progress updates
- `log_status_slot(self, message: str, level: str)` - Slot for status logging

**Modified Functions in MainWindow:**
- `validate_inputs(self, *args)` - Adapt to PyQt6 input widgets but keep same validation logic
- `start_conversion(self)` - Emit signal instead of calling callback
- `browse_output_path(self)` - Use QFileDialog instead of tkinter.filedialog
- `use_default_path(self)` - Same logic but update PyQt6 widgets
- `clear_status_log(self)` - Adapt to PyQt6 text widget

**New Functions in PreviewWindow:**
- `__init__(self, parent)` - Initialize QDialog with Qt components
- `init_ui(self)` - Set up PyQt6 interface with QTabWidget
- `setup_connections(self)` - Connect PyQt6 signals and slots
- `update_content(self)` - Update PyQt6 widgets with markdown content

**Modified Functions in PreviewWindow:**
- `show(self, markdown_content: str, file_path: str)` - Adapt to PyQt6 dialog
- `save_as(self)` - Use QFileDialog instead of tkinter.filedialog
- `save_copy(self)` - Use QFileDialog instead of tkinter.filedialog
- `copy_to_clipboard(self)` - Use QApplication.clipboard() instead of tkinter
- `close(self)` - Adapt to PyQt6 dialog closing

**Modified Functions in AppController:**
- `__init__(self)` - Initialize QApplication instead of Tkinter root
- `_setup_callbacks(self)` - Rename to `_setup_connections()` and use signal-slot connections
- `run(self)` - Adapt to PyQt6 application execution
- `shutdown(self)` - Adapt to PyQt6 application shutdown

**New Functions in AppController:**
- `_setup_connections(self)` - Connect PyQt6 signals to controller methods
- `handle_conversion_started(self, token: str, doc_id: str)` - Slot for conversion signal
- `handle_preview_requested(self)` - Slot for preview signal
- `handle_settings_requested(self)` - Slot for settings signal

**Modified Functions in main.py:**
- `check_dependencies(self)` - Add PyQt6 to required packages check
- `main()` - Initialize QApplication instead of Tkinter root

[Classes]
Completely rewrite GUI classes and adapt controller class for PyQt6 integration.

**New Classes:**
- `MainWindow(QMainWindow)` - Replaces Tkinter-based MainWindow
  - Inherits from PyQt6.QtWidgets.QMainWindow
  - Contains all same input fields, buttons, progress bar, and status display
  - Uses Qt layout managers (QVBoxLayout, QHBoxLayout, QFormLayout)
  - Implements signal-based communication instead of callbacks

- `PreviewWindow(QDialog)` - Replaces Tkinter-based PreviewWindow
  - Inherits from PyQt6.QtWidgets.QDialog
  - Uses QTabWidget for source code and preview tabs
  - Implements Qt text widgets with syntax highlighting
  - Uses Qt dialogs for file operations

- `SettingsWindow(QDialog)` - Replaces Tkinter-based SettingsWindow
  - Inherits from PyQt6.QtWidgets.QDialog
  - Uses QTabWidget for different setting categories
  - Implements Qt input widgets for all settings
  - Uses Qt file dialogs for directory selection

**Modified Classes:**
- `AppController` - Adapt for PyQt6 integration
  - Replace Tkinter root with QApplication
  - Replace callback setup with signal-slot connections
  - Keep all business logic methods unchanged
  - Adapt window management for Qt

**Removed Classes:**
- Original Tkinter-based `MainWindow` - Replaced by PyQt6 version
- Original Tkinter-based `PreviewWindow` - Replaced by PyQt6 version
- Original Tkinter-based `SettingsWindow` - Replaced by PyQt6 version

[Dependencies]
Update dependency configuration to ensure PyQt6 compatibility while preserving existing functionality.

**New Dependencies:**
- `PyQt6>=6.7.1` - Already present in pyproject.toml
- No additional dependencies required

**Dependency Version Changes:**
- No version changes needed for existing dependencies
- `lark-oapi>=1.2.0` - Keep as is
- `requests>=2.25.0` - Keep as is

**Integration Requirements:**
- Ensure PyQt6 is properly imported in all GUI modules
- Replace all tkinter imports with PyQt6 imports
- Update all widget creation and management code
- Adapt event handling from callbacks to signal-slot mechanism
- Ensure thread safety for PyQt6 GUI updates

[Testing]
Verify that all existing functionality works identically with the new PyQt6 interface.

**Test File Requirements:**
- Create `tests/gui/test_main_window.py` - Test all MainWindow functionality
- Create `tests/gui/test_preview_window.py` - Test all PreviewWindow functionality
- Create `tests/gui/test_app_controller.py` - Test signal-slot connections
- Create `tests/integration/test_full_workflow.py` - Test complete conversion workflow

**Existing Test Modifications:**
- No existing tests to modify (none found in codebase)

**Validation Strategies:**
- **Functional Testing:** Verify all input fields, buttons, and workflows work identically
- **Signal Testing:** Ensure all signals are properly emitted and connected
- **UI Testing:** Verify interface layout and behavior matches original
- **Integration Testing:** Test complete conversion process from input to output
- **Error Handling:** Verify all error cases are handled properly
- **File Operations:** Test all file save, browse, and preview functionality
- **Settings Testing:** Verify settings window and persistence work correctly

**Test Cases:**
1. Input validation (token format, document ID format)
2. Conversion workflow with valid credentials
3. Conversion workflow with invalid credentials
4. Progress bar updates during conversion
5. Status message logging and display
6. Preview window functionality
7. File save operations with various paths
8. Settings window functionality and persistence
9. Error handling and display
10. Application startup and shutdown

[Implementation Order]
Execute changes in a specific sequence to minimize disruption and ensure successful integration.

1. **Update Dependencies and Imports**
   - Verify PyQt6 is properly installed
   - Update main.py imports from tkinter to PyQt6
   - Update dependency checking logic

2. **Rewrite MainWindow Class**
   - Create new PyQt6-based MainWindow
   - Implement all input fields and buttons
   - Add signal definitions and emissions
   - Implement validation logic
   - Add progress bar and status display

3. **Rewrite PreviewWindow Class**
   - Create new PyQt6-based PreviewWindow
   - Implement tabbed interface
   - Add syntax highlighting for source code
   - Implement file operations with Qt dialogs

4. **Rewrite SettingsWindow Class**
   - Create new PyQt6-based SettingsWindow
   - Implement tabbed settings interface
   - Add all setting controls and validation

5. **Adapt AppController Class**
   - Replace Tkinter initialization with QApplication
   - Replace callback setup with signal-slot connections
   - Adapt window management methods
   - Ensure thread safety for GUI updates

6. **Update Main Application Entry**
   - Replace Tkinter root with QApplication
   - Update application startup and shutdown logic
   - Ensure proper exception handling

7. **Testing and Validation**
   - Test all individual components
   - Test complete workflow integration
   - Verify all error handling scenarios
   - Ensure functional parity with original application

8. **Documentation and Cleanup**
   - Update any relevant documentation
   - Clean up unused imports
   - Verify code quality and consistency
