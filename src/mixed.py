import yaml
import os
from typing import Dict, Any


def load_yaml(file_path: str) -> Dict[str, Any]:
    """加载YAML文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载文件 {file_path} 时出错: {e}")
        return None


def merge_yaml_configs(wifi_config: Dict[str, Any], base_config: Dict[str, Any]) -> Dict[str, Any]:
    """合并两个YAML配置"""
    if not wifi_config or not base_config:
        return None

    def merge_dicts(wifi_dict: Dict[str, Any], base_dict: Dict[str, Any]) -> Dict[str, Any]:
        result = base_dict.copy()
        for key, wifi_value in wifi_dict.items():
            if key not in result:
                result[key] = wifi_value
                continue
            base_value = result[key]
            if isinstance(wifi_value, dict) and isinstance(base_value, dict):
                result[key] = merge_dicts(wifi_value, base_value)
            elif isinstance(wifi_value, list) and isinstance(base_value, list):
                if key == 'rules':
                    wifi_rules = [
                        rule.strip() for rule in wifi_value
                        if isinstance(rule, str) and 'SRC-IP-CIDR' in rule]
                    result[key] = wifi_rules + base_value
                elif key == 'proxy-groups':
                    existing_names = {
                        group.get('name') for group in base_value
                        if isinstance(group, dict) and 'name' in group
                    }
                    new_groups = [group for group in wifi_value
                                  if group.get('name') not in existing_names]
                    result[key] = base_value + new_groups
                elif key == 'proxies':
                    existing_names = {
                        proxy.get('name') if isinstance(proxy, dict) else proxy
                        for proxy in base_value}
                    new_proxies = [
                        proxy for proxy in wifi_value
                        if (isinstance(proxy, dict) and proxy.get('name') not in existing_names)
                        or (not isinstance(proxy, dict) and proxy not in existing_names)]
                    result[key] = base_value + new_proxies
                else:
                    result[key] = base_value
            else:
                result[key] = wifi_value
        return result

    return merge_dicts(wifi_config, base_config)


def minimize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """最小化配置，移除不必要的内容"""
    # 移除所有注释
    if isinstance(config, dict):
        return {k: minimize_config(v) for k, v in config.items()
                if not k.startswith('#') and v is not None}
    elif isinstance(config, list):
        return [minimize_config(item) for item in config if item is not None]
    return config


def save_yaml(config: Dict[str, Any], output_path: str) -> None:
    """保存YAML配置，对特定项使用紧凑格式"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 最小化配置
        minimal_config = minimize_config(config)

        # 对特定的配置项进行紧凑格式处理
        if 'proxy-groups' in minimal_config:
            for group in minimal_config['proxy-groups']:
                if isinstance(group, dict) and 'proxies' in group:
                    # 将proxies列表转换为单行格式
                    group['proxies'] = [p.strip() if isinstance(
                        p, str) else p for p in group['proxies']]

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                minimal_config, f,
                default_flow_style=None,  # 让PyYAML自动决定
                allow_unicode=True,
                sort_keys=False,
                indent=2,
                width=float("inf"),  # 防止长行自动换行
                default_style=None
            )  # 不强制任何样式
        print(f"配置已保存到: {output_path}")
    except Exception as e:
        print(f"保存配置时出错: {e}")


def main():
    wifi_path = "mix-config/wifi-mixed.yaml"
    base_path = "miho-cfg.yaml"
    output_path = "mixed/miho-wifi-mixed.yml"

    wifi_config = load_yaml(wifi_path)
    base_config = load_yaml(base_path)
    merged_config = merge_yaml_configs(wifi_config, base_config)

    if merged_config:
        save_yaml(merged_config, output_path)
    else:
        print("合并配置失败")


if __name__ == "__main__":
    main()
