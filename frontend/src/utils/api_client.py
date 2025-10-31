"""
バックエンドAPI連携ユーティリティ
"""
import requests
from typing import Dict, Any, Optional, List
import os


class AIMEEAPIClient:
    """AIMEE BackendAPIクライアント"""

    def __init__(self, base_url: str = None):
        """
        Args:
            base_url: バックエンドAPIのベースURL（デフォルト: http://localhost:8002）
        """
        self.base_url = base_url or os.getenv("AIMEE_API_URL", "http://localhost:8002")
        self.api_v1 = f"{self.base_url}/api/v1"

    def get_alerts(self, priority: str = None, status: str = None) -> Dict[str, Any]:
        """
        アラート一覧を取得

        Args:
            priority: 優先度フィルタ（critical, high, medium, low）
            status: ステータスフィルタ（new, acknowledged, in_progress, resolved）

        Returns:
            アラート一覧
        """
        url = f"{self.api_v1}/alerts"
        params = {}
        if priority:
            params["priority"] = priority
        if status:
            params["status"] = status

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "alerts": [], "total": 0}

    def check_alerts(self) -> Dict[str, Any]:
        """
        アラート基準チェックを実行

        Returns:
            生成されたアラート一覧
        """
        url = f"{self.api_v1}/alerts/check"

        try:
            response = requests.get(url, timeout=120)  # 2分に延長
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "alert_count": 0, "alerts": []}

    def resolve_alert(self, alert_id: int) -> Dict[str, Any]:
        """
        アラートをAIで解消する提案を生成

        Args:
            alert_id: アラートID

        Returns:
            解消提案
        """
        url = f"{self.api_v1}/alerts/{alert_id}/resolve"

        try:
            response = requests.post(url, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def chat_with_ai(self, message: str, context: Dict[str, Any] = None, session_id: str = None, debug: bool = False) -> Dict[str, Any]:
        """
        統合LLMとチャット

        Args:
            message: ユーザーメッセージ
            context: コンテキスト情報
            session_id: セッションID（会話履歴用）
            debug: デバッグ情報を含めるか

        Returns:
            AI応答
        """
        url = f"{self.api_v1}/chat/message"
        payload = {
            "message": message,
            "context": context or {},
            "session_id": session_id or "default",
            "debug": debug
        }

        try:
            response = requests.post(url, json=payload, timeout=180)  # 3分に延長
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "response": "エラーが発生しました"}

    def rag_search(
        self,
        query: str,
        business_id: str = None,
        process_id: str = None,
        location_id: str = None,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        RAG検索を実行

        Args:
            query: 検索クエリ
            business_id: 業務ID
            process_id: 工程ID
            location_id: 拠点ID
            n_results: 検索結果数

        Returns:
            検索結果
        """
        url = f"{self.api_v1}/llm-test/rag-search"
        payload = {
            "query": query,
            "n_results": n_results
        }
        if business_id:
            payload["business_id"] = business_id
        if process_id:
            payload["process_id"] = process_id
        if location_id:
            payload["location_id"] = location_id

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "recommended_operators": []}

    def test_connection(self) -> bool:
        """
        バックエンドAPI接続テスト

        Returns:
            接続成功ならTrue
        """
        url = f"{self.api_v1}/llm-test/connection"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return True
        except:
            return False

    def get_pending_approvals(self, status: str = "pending", urgency: str = None) -> Dict[str, Any]:
        """
        承認待ち一覧を取得

        Args:
            status: ステータスフィルタ (pending, approved, rejected)
            urgency: 緊急度フィルタ (high, medium, low)

        Returns:
            承認待ち一覧
        """
        url = f"{self.api_v1}/approvals"
        params = {}
        if status:
            params["status"] = status
        if urgency:
            params["urgency"] = urgency

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "approvals": [], "total": 0}

    def get_approval_detail(self, approval_id: str) -> Dict[str, Any]:
        """
        承認詳細を取得

        Args:
            approval_id: 承認ID

        Returns:
            承認詳細情報
        """
        url = f"{self.api_v1}/approvals/{approval_id}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def execute_approval_action(
        self,
        approval_id: str,
        action: str,
        user: str = None,
        user_id: str = None,
        reason: str = None,
        notes: str = None
    ) -> Dict[str, Any]:
        """
        承認アクション実行 (承認/却下)

        Args:
            approval_id: 承認ID
            action: アクション ("approve" または "reject")
            user: ユーザー名
            user_id: ユーザーID
            reason: 承認/却下理由
            notes: 補足コメント

        Returns:
            実行結果
        """
        url = f"{self.api_v1}/approvals/{approval_id}/action"
        payload = {
            "action": action,
            "user": user,
            "user_id": user_id,
            "reason": reason,
            "notes": notes
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}

    def get_alert_detail(self, alert_id: int) -> Dict[str, Any]:
        """
        アラート詳細を取得

        Args:
            alert_id: アラートID

        Returns:
            アラート詳細情報
        """
        url = f"{self.api_v1}/alerts/{alert_id}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
