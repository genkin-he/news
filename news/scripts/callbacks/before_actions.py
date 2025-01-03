import os

def clear_action_errors_env_var():
    if "ACTION_ERRORS" in os.environ:
        os.environ["ACTION_ERRORS"] = ""
    print("环境变量 ACTION_ERRORS 已写入空值")

if __name__ == "__main__":
    try:
        clear_action_errors_env_var()
    except Exception as e:
        print(f"移除环境变量过程中发生错误: {str(e)}")
