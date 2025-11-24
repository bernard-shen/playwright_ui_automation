#!/usr/bin/python
# -*- coding: UTF-8 -*-
# --Author: Bernard--

import json
import yaml
import configparser
from pathlib import Path
import pandas as pd
from typing import Any, Dict, List, Union, Optional


class ConfigReader:
    """
    统一的配置数据读取工具类
    支持从JSON、YAML、INI配置文件和Excel文件中获取数据
    """
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        if base_path is None:
            current_file = Path(__file__)
            self.base_path = current_file.parent.parent / 'config'
        else:
            self.base_path = Path(base_path)
    
    def load_json(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> Any:
        """
        从JSON文件中获取数据
        """
        full_path = self._get_full_path(file_path)
        
        try:
            with open(full_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON文件不存在: {full_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"JSON格式错误: {e}", e.doc, e.pos)
    
    def load_yaml(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> Any:
        """
        从YAML文件中获取数据
        """
        full_path = self._get_full_path(file_path)
        
        try:
            with open(full_path, 'r', encoding=encoding) as f:
                data = yaml.safe_load(f.read())
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML文件不存在: {full_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML格式错误: {e}")
    
    def get_ini_conf(self, file_path: Union[str, Path], section: str, key: str, encoding: str = 'utf-8') -> str:
        """
        从INI、CONF配置文件中获取指定section和key的值---两层结构
        
        Args:
            file_path: INI文件路径
            section: 配置节名称
            key: 配置键名称
            encoding: 文件编码，默认utf-8
            
        Returns:
            配置值
            
        Raises:
            KeyError: section或key不存在
        """
        full_path = self._get_full_path(file_path)
        
        try:
            config = configparser.ConfigParser()
            config.read(full_path, encoding=encoding)
        except FileNotFoundError:
            raise FileNotFoundError(f"INI文件不存在: {full_path}")
        except configparser.Error as e:
            raise configparser.Error(f"INI格式错误: {e}")

        if not config.has_section(section):
            raise KeyError(f"配置节不存在: {section}")
        
        if not config.has_option(section, key):
            raise KeyError(f"配置键不存在: {section}.{key}")
        
        return config.get(section, key)
    
    def get_ini_conf_list(self, file_path: Union[str, Path], section: str, key: str, encoding: str = 'utf-8') -> List[str]:
        """
        从INI、CONF配置文件中获取列表格式的值
        """
        value = self.get_ini_value(file_path, section, key, encoding)
        # 移除方括号并分割
        clean_value = value.strip('[]')
        return [item.strip() for item in clean_value.split(',')]
    
    def load_excel(self, file_path: Union[str, Path], sheet_name: Union[str, int] = 0, 
                   header: Optional[Union[int, List[int]]] = 0, 
                   usecols: Optional[Union[str, List[str], List[int]]] = None) -> pd.DataFrame:
        """
        从Excel文件中获取数据
        """
        full_path = self._get_full_path(file_path)
        
        try:
            df = pd.read_excel(
                full_path,
                sheet_name=sheet_name,
                header=header,
                usecols=usecols
            )
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel文件不存在: {full_path}")
        except Exception as e:
            raise ValueError(f"Excel文件读取错误: {e}")
    
    def get_excel_data(self, file_path: Union[str, Path], sheet_name: Union[str, int] = 0,
                      header: Optional[Union[int, List[int]]] = 0) -> List[Dict[str, Any]]:
        """
        从Excel文件中获取数据并转换为字典列表格式
        """
        df = self.load_excel(file_path, sheet_name, header)
        return df.to_dict('records')
    
    def get_yaml_location(self, file_path: Union[str, Path], page_name: str, module_name: str, 
                         encoding: str = 'utf-8') -> Any:
        """
        从YAML文件中获取指定页面和模块的定位器数据（类似原get_location的功能）
        
        Args:
            file_path: YAML文件路径
            page_name: 页面名称
            module_name: 模块名称
            encoding: 文件编码
            
        Returns:
            定位器数据
            
        Raises:
            KeyError: 页面或模块不存在
        """
        data = self.load_yaml(file_path, encoding)
        
        if page_name not in data:
            raise KeyError(f"页面不存在: {page_name}")
        
        if module_name not in data[page_name]:
            raise KeyError(f"模块不存在: {page_name}.{module_name}")
        
        return data[page_name][module_name]
    
    def _get_full_path(self, file_path: Union[str, Path]) -> Path:
        """
        获取文件的完整路径
        """
        file_path = Path(file_path)
        if file_path.is_absolute():
            return file_path
        else:
            return self.base_path / file_path



class WebUIConfReader:
    __instance = None
    __inited = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if self.__inited is None:
            current_file = Path(__file__)
            config_path = current_file.parent.parent / 'config' / 'web_ui.conf'
            self.config = self._read_config(config_path)
            self.__inited = True

    def _read_config(self, config_file: Path) -> Dict[str, Any]:
        """
        读取web_ui.conf配置文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            包含配置信息的字典
        """
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(config_file, encoding='utf-8')
        
        web_ui_config = {
            'test_workers': config.get('test', 'test_workers'),
            'test_browsers': config.get('browser', 'test_browsers').split('||'),
            'current_browser': config.get('browser', 'current_browser'),
            'download_dir': config.get('browser', 'download_dir'),
            'is_headed': config.getboolean('browser', 'is_headed'),
            'slowmo': config.getint('browser', 'slowmo'),
            'trace': config.get('browser', 'trace'),

        }
        if config.has_section('pages'):
            web_ui_config['pages'] = dict(config.items('pages'))
        
        return web_ui_config


# 使用示例
if __name__ == '__main__':

    config_reader = ConfigReader()
    web_ui_conf_reader = WebUIConfReader()
    print(web_ui_conf_reader.config)

    # try:
    #     locations = config_reader.get_yaml_location('adts_locations.yaml', "系统配置-参数配置", '脱敏参数')
    #     print("YAML定位器数据:", locations)
    # except Exception as e:
    #     print(f"读取YAML数据失败: {e}")