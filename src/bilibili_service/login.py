"""
B站登录模块
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

def bilibili_login(username, password):
    """
    B站登录功能
    
    Args:
        username: 用户名/手机号
        password: 密码
        
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
        
        print("正在打开B站登录页面...")
        # 打开B站登录页面
        driver.get("https://passport.bilibili.com/login")
        
        # 等待页面加载
        time.sleep(3)
        
        try:
            # 等待页面加载完成
            print("等待登录页面加载...")
            time.sleep(3)
            
            # 输入用户名 - 根据实际HTML结构调整选择器
            print("输入用户名...")
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入账号']"))
            )
            username_input.clear()
            username_input.send_keys(username)
            
            # 输入密码
            print("输入密码...")
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入密码']"))
            )
            password_input.clear()
            password_input.send_keys(password)
            
            # 点击登录按钮 - 根据实际HTML结构调整选择器
            print("点击登录按钮...")
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_primary"))
            )
            
            # 检查按钮是否被禁用
            if "disabled" in login_button.get_attribute("class"):
                print("⚠️ 登录按钮被禁用，等待输入完成...")
                time.sleep(2)
            
            # 移除disabled属性并点击
            driver.execute_script("arguments[0].removeAttribute('disabled');", login_button)
            login_button.click()
            
            # 等待登录结果
            print("等待登录结果...")
            time.sleep(5)
            
            # 检查是否登录成功 - 通过URL跳转或页面元素判断
            current_url = driver.current_url
            print(f"当前URL: {current_url}")
            
            # 如果跳转到首页或者包含用户信息，说明登录成功
            if "bilibili.com" in current_url and "passport.bilibili.com" not in current_url:
                print("✅ 登录成功！")
                return True
            elif "passport.bilibili.com" in current_url:
                # 检查是否有验证码或其他验证
                try:
                    # 查找验证码相关元素
                    captcha_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'captcha')]")
                    if captcha_elements:
                        print("⚠️  检测到验证码，需要手动处理")
                        # 等待用户手动处理验证码
                        input("请手动完成验证码验证后按回车键继续...")
                        time.sleep(3)
                        # 再次检查登录状态
                        current_url = driver.current_url
                        if "bilibili.com" in current_url and "passport.bilibili.com" not in current_url:
                            print("✅ 登录成功！")
                            return True
                except:
                    pass
                
                print("❌ 登录失败，仍在登录页面")
                return False
            else:
                print("✅ 登录成功！")
                return True
                
        except Exception as e:
            print(f"❌ 登录过程中出现错误: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 初始化浏览器时出错: {e}")
        return False
        
    finally:
        if driver:
            # 保持浏览器打开一段时间查看结果
            print("浏览器将在10秒后关闭...")
            time.sleep(10)
            driver.quit()

def main():
    """主函数"""
    print("=== B站登录程序 ===")
    
    # 登录信息
    username = "13414727670"
    password = "hwz@1234"
    
    print(f"使用账号: {username}")
    print("开始登录...")
    
    # 执行登录
    success = bilibili_login(username, password)
    
    if success:
        print("🎉 登录完成！")
    else:
        print("😞 登录失败，请检查账号密码或网络连接")

if __name__ == "__main__":
    main()