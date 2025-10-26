#!/bin/bash
# Q1~Q6のAPIテストスクリプト

API_URL="http://localhost:8002/api/v1/chat/message"

echo "=== AIMEE API テスト (Q1~Q6) ==="
echo ""

# Q1: 納期20分前に処理完了
echo "【Q1】納期20分前に処理完了"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。",
    "context": {},
    "detail": false
  }' 2>/dev/null | jq -r '.response' | head -20

echo ""
echo "---"
echo ""

# Q2: 移動元への影響
echo "【Q2】移動元の処理に影響はありますか?"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "配置転換元の工程は大丈夫ですか? 移動元の処理に影響はありますか?",
    "context": {},
    "detail": false
  }' 2>/dev/null | jq -r '.response' | head -20

echo ""
echo "---"
echo ""

# Q3: 業務間移動
echo "【Q3】16:40受信分を優先処理"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SSの16:40受信分を優先的に処理したいです。非SSから何人移動させたらよいですか?",
    "context": {},
    "detail": false
  }' 2>/dev/null | jq -r '.response' | head -20

echo ""
echo "---"
echo ""

# Q4: 処理完了時刻予測
echo "【Q4】処理完了時刻の予測"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか",
    "context": {},
    "detail": false
  }' 2>/dev/null | jq -r '.response' | head -20

echo ""
echo "---"
echo ""

# Q5: 工程別最適配置
echo "【Q5】工程別最適配置"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "あはきを16:40頃までに処理完了させるためには各工程何人ずつ配置したら良いですか",
    "context": {},
    "detail": false
  }' 2>/dev/null | jq -r '.response' | head -20

echo ""
echo "---"
echo ""

# Q6: 遅延リスク検出
echo "【Q6】遅延リスク検出"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "現在の配置でそれぞれの納期までに遅延が発生する見込みがある工程はありますか",
    "context": {},
    "detail": false
  }' 2>/dev/null | jq -r '.response' | head -20

echo ""
echo "---"
echo "テスト完了"
