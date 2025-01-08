from gui.app import App
import sys
import traceback
import os

def show_error(error_msg):
    # 确保错误信息被打印和保存
    print("\n" + "="*50)
    print("错误信息:")
    print("="*50)
    print(error_msg)
    print("="*50)
    
    # 保存到日志文件
    try:
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        error_file = os.path.join(app_dir, 'error_log.txt')
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error_msg)
        print(f"\n错误日志已保存到: {error_file}")
    except Exception as e:
        print(f"保存错误日志失败: {str(e)}")
    
    return 1

def main():
    try:
        app = App()
        return app.run()
    except Exception as e:
        error_msg = f"错误信息：\n{str(e)}\n\n详细堆栈：\n{traceback.format_exc()}"
        return show_error(error_msg)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        error_msg = f"未捕获的错误：\n{str(e)}\n\n详细堆栈：\n{traceback.format_exc()}"
        sys.exit(show_error(error_msg))
