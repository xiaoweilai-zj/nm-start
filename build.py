import PyInstaller.__main__
import os
import shutil

def clean_build_folders():
    """清理构建文件夹"""
    folders = ['build', 'dist']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"已删除 {folder} 文件夹")

def build():
    """执行打包"""
    print("开始打包...")
    
    # 清理旧的构建文件
    clean_build_folders()
    
    # 使用 spec 文件打包
    PyInstaller.__main__.run([
        'NM启动器.spec',
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不询问确认
    ])
    
    print("打包完成！")
    print("可执行文件位于 dist 目录下")

if __name__ == "__main__":
    build() 