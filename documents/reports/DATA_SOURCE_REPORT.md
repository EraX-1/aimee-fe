# データソース状況レポート

**作成日**: 2025-10-16
**対象**: データベースとChromaDBの状況確認

---

## 📊 データベース (MySQL) の状況

### ✅ 実データが投入済み

**状況**: 名前だけモック化した実データが投入されています

| データ種別 | 件数 | データソース | 状態 |
|-----------|------|-------------|------|
| **拠点マスタ** | 7件 | location.csv | ✅ 実データ |
| **業務マスタ** | 12件 | business.csv | ✅ 実データ |
| **工程マスタ** | 78件 | project.csv | ✅ 実データ |
| **オペレータマスタ** | 2,664名 | operatorinfo.csv | ✅ **名前のみモック化** |
| **処理可能工程** | 55,863件 | oprprocessplan2.csv | ✅ 実データ |
| **作業実績** | 10,000件 | 523_operworktotal_V2.tsv | ✅ 実データ |
| **進捗スナップショット** | 832件 | KENPO_FS_*.csv | ✅ 実データ |
| **拠点別ログイン** | 68件 | KENPO_RWLOGIN_LOCATION_*.csv | ✅ 実データ |

### モック化された名前の例
- 井村 美子
- 鈴木 一郎
- 田中 花子
- 佐藤 太郎
- など

**投入スクリプト**: `/Users/umemiya/Desktop/erax/aimee-db/import_all_real_data.py`

---

## 🔍 ChromaDB (RAGベクトルDB) の状況

### ✅ 投入状態が判明!

#### ChromaDBの内容 (aimee-beリポジトリ調査結果)

**コレクション**: `aimee_knowledge`

| データタイプ | 件数 | 説明 |
|------------|------|------|
| **オペレータチャンク** | 25,718件 | 2,591名のオペレータ情報 |
| **工程チャンク** | 88件 | 78工程の情報 |
| **管理者ルール** | 未確認 | MySQLのrag_contextから投入予定? |
| **総ドキュメント数** | **25,829件** | |

**投入スクリプト**: `/Users/umemiya/Desktop/erax/aimee-be/app/services/chroma_service.py:202-240` (バッチ処理機能)

**投入済みの確認方法**:
```bash
curl http://localhost:8003/api/v1/collections/aimee_knowledge
```

---

### MySQLの`rag_context`テーブル

**場所**: MySQLの`aimee_db.rag_context`

**投入済みデータ**: 5件以上

| context_type | context_key | 内容 |
|------------|------------|------|
| `manager_rule` | 拠点担当業務 | 佐世保：適用徴収、札幌：SS/あはき、品川：SS片道/あはき |
| `manager_rule` | SS受領大量時対応 | 1,000件以上の場合、納品1時間前で未完了なら人員を寄せる |
| `manager_rule` | 再々識別リスク | SS片道はイメージ不備が多く再々識別に落ちやすい |
| `past_pattern` | 拠点別補正しきい値 | 品川：50件、大阪：100件以上で補正に人員配置 |
| `past_pattern` | 毎時処理パターン | 毎時40分に案件受領、エントリーまでラグ発生 |

**合計**: 約14件 (IMPLEMENTATION_SUMMARY.mdより)

### データソース

**投入方法**: `/Users/umemiya/Desktop/erax/aimee-db/import_real_data.py:361-395`

```python
def import_manager_rules(self):
    """管理者ルールをRAGコンテキストに完全反映"""
    # 管理者の判断材料テキストから詳細なルールを抽出して投入
    rules = [
        # 配置ルール
        ('placement_rule', '長時間配置制限', '1つの工程に30分以上1時間未満の配置。長時間配置すると集中力低下', 0.95),
        ('placement_rule', '同一人物コンペア禁止', 'エントリ1≠エントリ2≠補正≠SV補正。1帳票で同一人物が複数工程を担当しない', 0.95),

        # 業務ルール
        ('business_rule', '佐世保担当', '佐世保：適用徴収、適用徴収片道、非SS片道', 0.90),
        ('business_rule', '札幌エントリ優先', '札幌でエントリ1が遅延した場合は他拠点からの応援を優先検討', 0.90),

        # タイミングルール
        ('timing_rule', '通常業務配置タイミング', '08:45~09:00 (朝礼後)、12:15~12:30、18:15~18:30', 0.85),
        ('timing_rule', '緊急配置タイミング', '納品30分前から逆算して人員不足が予測される場合', 0.90),

        # ワークフロールール
        ('workflow_rule', '再識別フロー', 'OCR判別不可の帳票は再識別フローへ。人の目で判断し正しいフローへ遷移', 0.85),
        ('workflow_rule', '再々識別フロー', 'エントリ中の画像不備は再々識別へ。人の目で帳票判別', 0.85)
    ]
```

**重要**: これらのルールは**コード内にハードコードされています**

### 元のデータソースについて

**実際の状況 (aimee-beリポジトリで判明)**:
- ✅ ChromaDBには**25,829ドキュメント**が投入済み (オペレータ情報)
- ✅ MySQLの`rag_context`テーブルに**14件**の管理者ルールが投入済み
- ❓ ChromaDBに管理者ルールも投入されているかは未確認

**詳細ドキュメント**:
- `/Users/umemiya/Desktop/erax/aimee-be/IMPLEMENTATION_SUMMARY.md`
- `/Users/umemiya/Desktop/erax/aimee-be/DEMO_COMMANDS.md`
- `/Users/umemiya/Desktop/erax/aimee-be/DEMO_RESULTS.md`

---

## 🔧 ChromaDBの役割

### 設計上の想定

ChromaDBは以下を格納する予定でした:
1. **オペレータ情報のセマンティックチャンク** (未投入)
2. **過去の配置変更パターン** (未投入)
3. **管理者ノウハウ** (未投入)

### 現在の実装

**ファイル**: `/Users/umemiya/Desktop/erax/aimee-be/app/services/chroma_service.py`

```python
class ChromaService:
    """ChromaDBとのインタラクションを管理するサービス"""

    def create_operator_chunks(self, operator, capabilities):
        """オペレータ情報をセマンティックチャンクに分割"""
        # 実装済みだが、データ投入はされていない
```

**状態**:
- コレクション名: `aimee_knowledge`
- データ投入: **未実行**
- 接続先: `chromadb:8000` (Dockerコンテナ)

---

## 📋 現在のRAG検索の動作

### integrated_llm_service.py での使用

**ファイル**: `/Users/umemiya/Desktop/erax/aimee-be/app/services/integrated_llm_service.py:64-105`

```python
# ChromaServiceを遅延初期化
if not self._chroma_initialized:
    try:
        self._chroma_service = ChromaService()
        self._chroma_initialized = True
        app_logger.info("ChromaDB初期化成功")
    except Exception as e:
        app_logger.warning(f"ChromaDB初期化失敗: {e}")
        self._chroma_service = None
        self._chroma_initialized = True  # 再試行しない

if self._chroma_service:
    # セマンティック検索でコンテキスト情報を取得
    similar_docs = self._chroma_service.query_similar(
        query_text=query_text,
        n_results=3
    )
else:
    app_logger.info("ChromaDB未初期化のためRAG検索スキップ")
```

**動作**:
- ChromaDBの初期化に失敗した場合は**スキップ**される
- エラーになっても処理は継続する

---

## 🎯 管理者ノウハウの実際の使用箇所

### MySQLの`rag_context`テーブル

**使用箇所**: 現在は**使用されていません**

**理由**:
- `integrated_llm_service.py`はChromaDBからRAG検索を試みる
- MySQLの`rag_context`テーブルは直接参照されていない

**確認方法**:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT * FROM rag_context')
for row in result:
    print(row)
"
```

---

## ✅ 推奨される対応

### オプション1: ChromaDBに管理者ノウハウを投入 (推奨)

**手順**:

1. **投入スクリプトを作成**

```python
# /Users/umemiya/Desktop/erax/aimee-db/import_chroma_knowledge.py
import chromadb
from config import db_manager

# ChromaDBクライアント
client = chromadb.HttpClient(host='localhost', port=8003)
collection = client.get_or_create_collection(name="aimee_knowledge")

# MySQLからrag_contextを取得
result = db_manager.execute_query("SELECT * FROM rag_context")

# ChromaDBに投入
documents = []
metadatas = []
ids = []

for i, row in enumerate(result):
    documents.append(row['context_value'])
    metadatas.append({
        'type': row['context_type'],
        'key': row['context_key'],
        'relevance_score': float(row['relevance_score'])
    })
    ids.append(f"rule_{i}")

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print(f"ChromaDBに{len(documents)}件のルールを投入しました")
```

2. **実行**

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 import_chroma_knowledge.py
```

---

### オプション2: MySQLのrag_contextを直接参照 (簡易対応)

**修正箇所**: `/Users/umemiya/Desktop/erax/aimee-be/app/services/integrated_llm_service.py`

```python
# ChromaDB検索の後にMySQLからも取得
if not rag_results.get("similar_context"):
    # ChromaDBが使えない場合はMySQLから取得
    mysql_rules = await self._get_mysql_rag_rules(db, message)
    rag_results["similar_context"] = mysql_rules
```

---

### オプション3: 管理者ノウハウのテキストファイルを用意 (長期対応)

**ファイル作成**: `/Users/umemiya/Desktop/erax/TC_DATA_RealWorksManager/管理者の判断材料.txt`

```txt
【配置ルール】
1. 長時間配置制限
1つの工程に30分以上1時間未満の配置。長時間配置すると集中力低下。

2. 同一人物コンペア禁止
エントリ1≠エントリ2≠補正≠SV補正。1帳票で同一人物が複数工程を担当しない。

【業務ルール】
3. 佐世保担当
佐世保：適用徴収、適用徴収片道、非SS片道

4. 札幌エントリ優先
札幌でエントリ1が遅延した場合は他拠点からの応援を優先検討

...
```

その後、ChromaDBに投入するスクリプトを作成。

---

## 📌 まとめ

| 項目 | 状態 | データソース |
|------|------|------------|
| **MySQLデータ** | ✅ 投入済み | 実データ (名前のみモック) |
| **管理者ノウハウ (MySQL)** | ✅ 投入済み | コード内ハードコード (14件) |
| **ChromaDB (オペレータ)** | ✅ 投入済み | 25,718件のオペレータチャンク |
| **ChromaDB (工程)** | ✅ 投入済み | 88件の工程チャンク |
| **ChromaDB (管理者ルール)** | ❓ 未確認 | 要確認 |

### 現在の動作 (aimee-beリポジトリの情報)

- AIの配置提案は**MySQLのリアルタイムデータ + ChromaDBのRAG検索**を使用
- 管理者ノウハウはMySQLの`rag_context`テーブルに**14件投入済み**
- ChromaDBには**25,829ドキュメント**が投入済み (主にオペレータ情報)

### 詳細ドキュメント (aimee-beリポジトリ)

- `/Users/umemiya/Desktop/erax/aimee-be/IMPLEMENTATION_SUMMARY.md` - 実装完了報告
- `/Users/umemiya/Desktop/erax/aimee-be/DEMO_COMMANDS.md` - デモ用コマンド集
- `/Users/umemiya/Desktop/erax/aimee-be/DEMO_RESULTS.md` - デモ実行結果

### 推奨アクション

1. **即座**: MySQLの`rag_context`を直接参照するよう修正 (オプション2)
2. **短期**: ChromaDBに管理者ノウハウを投入 (オプション1)
3. **長期**: 管理者ノウハウのテキストファイルを整備 (オプション3)

---

**レポート終了**
