import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger, get_logger

logger = get_logger(__name__)

def main():
    """主程序入口 - 现代化版本"""
    try:
        logger.info("🚀 启动A股投资分析工具 v2.0 (现代化版本)")
        
        # 设置高DPI支持 - 使用PyQt6兼容的方式
        try:
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
        except AttributeError:
            pass  # 如果属性不存在，忽略
        
        try:
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # PyQt6 新版本中这些属性可能已经被移除或改名
            pass
        
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("A股投资分析工具")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("QuantAnalyzer")
        
        # 设置默认字体
        font = QFont("Microsoft YaHei", 9)
        app.setFont(font)
        
        # 设置应用程序图标
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "app.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        # 初始化日志
        setup_logger()
        
        # 创建并显示主窗口
        main_window = MainWindow()
        main_window.show()
        
        logger.info("✅ 主窗口显示成功")
        
        # 启动应用程序
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        
        # 如果GUI初始化失败，显示错误对话框
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            QMessageBox.critical(None, "启动错误", f"程序启动失败:\n{e}")
        except Exception as e:
            print(f"严重错误: {e}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
