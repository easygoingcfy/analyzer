import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger

def main():
    """主程序入口"""
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
    app.setApplicationVersion("1.0.0")
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
    
    # 启动应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
