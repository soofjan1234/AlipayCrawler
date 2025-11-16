"""
简单的Selenium脚本 - 打开B站页面
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import platform
import os

def get_chrome_options(headless=False, profile_name="Default"):
    """
    配置Chrome浏览器选项，提供跨平台兼容的浏览器配置
    
    Args:
        headless: 是否启用无头模式
        profile_name: Chrome配置文件名称
        
    Returns:
        Options: 配置好的ChromeOptions实例
    """
    from selenium.webdriver.chrome.options import Options
    
    # 创建Chrome浏览器实例
    options = Options()
    options.add_argument("--start-maximized")
    
    # 设置无头模式（如果需要）
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    
    # 根据不同操作系统设置不同的Chrome配置文件路径
    system = platform.system()
    user_home = os.path.expanduser("~")
    
    if system == "Windows":
        # Windows系统路径
        chrome_profile_path = "C:\\Users\\hou\\AppData\\Local\\Google\\selenium_profile"
        print(f"[浏览器配置] Windows系统，使用Chrome配置路径: {chrome_profile_path}")
    elif system == "Darwin":  # macOS
        # macOS系统路径
        chrome_profile_path = os.path.join(user_home, "Library", "Application Support", "Google", "Chrome", "selenium_profile")
        print(f"[浏览器配置] macOS系统，使用Chrome配置路径: {chrome_profile_path}")
    else:
        # 其他系统（如Linux）的默认路径
        chrome_profile_path = os.path.join(user_home, ".config", "google-chrome", "selenium_profile")
        print(f"[浏览器配置] {system}系统，使用Chrome配置路径: {chrome_profile_path}")
    
    # 确保配置文件目录存在
    os.makedirs(chrome_profile_path, exist_ok=True)
    
    # 设置用户数据目录
    options.add_argument(f"--user-data-dir={chrome_profile_path}")
    
    # 设置独立的profile名称（避免与系统Chrome冲突）
    options.add_argument(f"--profile-directory={profile_name}")
    
    return options

def open_bilibili():
    """打开B站首页"""
    # 获取Chrome配置
    chrome_options = get_chrome_options()
    
    try:
        # 初始化Chrome浏览器 - 尝试直接使用系统Chrome
        driver = webdriver.Chrome(options=chrome_options)
    except:
        try:
            # 如果失败，尝试使用webdriver-manager
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        except:
            # 最后尝试不使用任何配置
            driver = webdriver.Chrome()
    
    try:
        # 打开B站首页
        driver.get("https://space.bilibili.com/420831218/dynamic")
        
        # 等待页面加载
        time.sleep(15)
        
        print("B站页面已成功打开")
        
        # 保持浏览器打开5秒
        time.sleep(15)
        
    except Exception as e:
        print(f"打开B站页面时出错: {e}")
        
    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == "__main__":
    open_bilibili()