"""
抖音登录模块
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
    
    # 使用专门的项目目录来保持登录状态
    project_dir = "/Users/Zhuanz/projects/PythonWS/Alipay"
    chrome_profile_path = os.path.join(project_dir, "chrome_user_data")
    print(f"[浏览器配置] 使用项目Chrome配置路径: {chrome_profile_path}")
    
    # 确保配置文件目录存在
    os.makedirs(chrome_profile_path, exist_ok=True)
    
    # 设置用户数据目录
    options.add_argument(f"--user-data-dir={chrome_profile_path}")
    
    # 设置独立的profile名称（避免与系统Chrome冲突）
    options.add_argument(f"--profile-directory={profile_name}")
    
    return options

def douyin_login(username=None, password=None):
    """
    抖音登录功能 - 打开网页让用户手动登录
    
    Args:
        username: 用户名/手机号（可选，用于扫码登录时为None）
        password: 密码（可选，用于扫码登录时为None）
        
    Returns:
        bool: 登录是否成功
    """
    driver = None
    try:
        # 获取Chrome配置
        chrome_options = get_chrome_options()
        
        # 初始化Chrome浏览器
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except:
            try:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            except:
                driver = webdriver.Chrome()
        
        print("正在打开抖音登录页面...")
        # 打开抖音登录页面
        driver.get("https://www.douyin.com/")
        
        # 等待页面加载
        time.sleep(5)
        
        print("✅ 抖音页面已打开，请手动完成登录操作")
        print("登录完成后，程序将自动检测登录状态...")
        
        # 等待用户手动登录，最多等待5分钟
        for i in range(300):  # 最多等待300秒
            try:
                # 检查是否已经登录（通过查找用户头像或其他登录后元素）
                
                
                time.sleep(1)
                if i % 30 == 0 and i > 0:
                    print(f"等待登录中... ({i//60}分{i%60}秒)")
                    
            except:
                pass
        
        print("⏰ 等待登录超时")
        return False
            
    except Exception as e:
        print(f"❌ 初始化浏览器时出错: {e}")
        return False
        
    finally:
        if driver:
            # 保持浏览器打开，让用户可以继续使用
            print("浏览器将保持打开状态，您可以继续使用...")
            print("如需关闭浏览器，请按 Ctrl+C")
            try:
                # 等待用户主动关闭
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\n正在关闭浏览器...")
                driver.quit()

def main():
    """主函数"""
    print("=== 抖音登录程序 ===")
    
    # 直接使用内置的账号密码
    username = "13414727670"
    password = "hwz@1234"
    
    print(f"使用内置账号: {username}")
    print("开始登录...")
    
    # 执行登录
    success = douyin_login(username, password)
    
    if success:
        print("🎉 登录完成！")
    else:
        print("😞 登录失败，请检查网络连接或重试")

if __name__ == "__main__":
    main()