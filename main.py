import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from utils.logger import logger
from config import APP_NAME
import traceback

def main():
    """Main application entry point"""
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    logger.info("="*50)
    logger.info(f"Application starting: {APP_NAME}")
    logger.info("="*50)
    
    # Keep reference to main window (prevent garbage collection)
    main_window = None
    
    # Show login window
    login_window = LoginWindow()
    
    def on_login_success(user_data):
        """Handle successful login"""
        nonlocal main_window  # Use nonlocal to modify outer variable
        
        try:
            logger.info(f"User logged in: {user_data['username']}")
            
            # Show main window
            logger.info("Creating main window...")
            main_window = MainWindow()
            logger.info("Main window created successfully")
            
            main_window.show()
            logger.info("Main window displayed")
            
        except Exception as e:
            logger.error(f"Error creating main window: {e}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(None, "Error", f"Failed to open main window:\n\n{str(e)}\n\nCheck logs for details.")
    
    login_window.login_successful.connect(on_login_success)
    login_window.show()
    
    # Run application
    sys.exit(app.exec_())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}")
        logger.error(traceback.format_exc())
        print(f"ERROR: {e}")
