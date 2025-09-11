import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional

class DataLoader:
    def __init__(self, data_path: str = "../10_KenpoRealWorksManager_R5SS/Data"):
        self.data_path = data_path
        
    def load_latest_file(self, file_pattern: str) -> Optional[pd.DataFrame]:
        """指定されたパターンに一致する最新のファイルを読み込む"""
        try:
            files = [f for f in os.listdir(self.data_path) if f.startswith(file_pattern)]
            if not files:
                return None
                
            latest_file = sorted(files)[-1]
            file_path = os.path.join(self.data_path, latest_file)
            
            return pd.read_csv(file_path, encoding='shift_jis')
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
    
    def load_flowscope_data(self) -> Optional[pd.DataFrame]:
        """FlowScope統合データ（KENPO_FS）を読み込む"""
        return self.load_latest_file("KENPO_FS_")
    
    def load_notinput_data(self) -> Optional[pd.DataFrame]:
        """未投入データ（KENPO_NOTINPUT）を読み込む"""
        return self.load_latest_file("KENPO_NOTINPUT_")
    
    def load_msgcount_data(self) -> Optional[pd.DataFrame]:
        """工程別未処理件数（KENPO_RWMSGCOUNT）を読み込む"""
        return self.load_latest_file("KENPO_RWMSGCOUNT_")
    
    def load_login_data(self) -> Optional[pd.DataFrame]:
        """ログインオペレータ数（KENPO_RWLOGIN）を読み込む"""
        return self.load_latest_file("KENPO_RWLOGIN_")
    
    def load_location_data(self) -> Optional[pd.DataFrame]:
        """拠点別配置・生産性（KENPO_RWLOGIN_LOCATION）を読み込む"""
        return self.load_latest_file("KENPO_RWLOGIN_LOCATION_")
    
    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """すべてのデータを読み込んで辞書形式で返す"""
        data = {
            "flowscope": self.load_flowscope_data(),
            "notinput": self.load_notinput_data(),
            "msgcount": self.load_msgcount_data(),
            "login": self.load_login_data(),
            "location": self.load_location_data()
        }
        
        return {k: v for k, v in data.items() if v is not None}
    
    def get_locations(self) -> List[str]:
        """拠点リストを取得"""
        return ["札幌", "盛岡", "品川", "西梅田", "本町東", "沖縄", "佐世保", "和歌山"]
    
    def get_processes(self) -> List[str]:
        """工程リストを取得"""
        return ["OCR", "エントリ1", "エントリ2", "補正", "SV補正", "目検"]