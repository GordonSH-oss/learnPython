import yaml
import os


def print_dict(data, prefix="", indent=0):
    """递归打印字典，格式化输出"""
    indent_str = "  " * indent
    
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            # 显示完整路径
            print(f"{indent_str}{full_key}:")
            print_dict(value, full_key, indent + 1)
        else:
            # 根据值的类型格式化输出
            if isinstance(value, str):
                print(f"{indent_str}{full_key}: {value!r}")
            elif isinstance(value, bool):
                print(f"{indent_str}{full_key}: {value}")
            elif isinstance(value, (int, float)):
                print(f"{indent_str}{full_key}: {value}")
            elif value is None:
                print(f"{indent_str}{full_key}: null")
            else:
                print(f"{indent_str}{full_key}: {value}")


def load_config(config_path="config.yaml"):
    """从 YAML 文件加载配置"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


if __name__ == "__main__":
    # 从外部 YAML 文件加载配置
    data = load_config("config.yaml")
    print_dict(data)