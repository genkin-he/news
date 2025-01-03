import os

def remove_action_errors_env_var():
    if 'ACTION_ERRORS' in os.environ:
        del os.environ['ACTION_ERRORS']
        print("环境变量 ACTION_ERRORS 已移除")
    else:
        print("环境变量 ACTION_ERRORS 不存在")

if __name__ == "__main__":
    try:
        remove_action_errors_env_var()
    except Exception as e:
        print(f"移除环境变量过程中发生错误: {str(e)}")

