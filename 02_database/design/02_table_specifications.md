# データベーステーブル仕様書

## 1. 共通マスタテーブル

### 1.1 locations（拠点マスタ）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| location_id | VARCHAR(10) | PK | 拠点ID（LOC001等） |
| location_name | VARCHAR(100) | NOT NULL | 拠点名（札幌センター等） |
| region | VARCHAR(50) | | 地域名（北海道、東北等） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

### 1.2 business_types（業務マスタ）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| business_id | VARCHAR(20) | PK | 業務ID（BUS001等） |
| business_name | VARCHAR(100) | NOT NULL | 業務名（健康保険申請等） |
| description | TEXT | | 業務の詳細説明 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

### 1.3 processes（工程マスタ）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| process_id | VARCHAR(20) | PK | 工程ID（PROC001等） |
| business_id | VARCHAR(20) | NOT NULL, FK | 所属業務ID |
| process_name | VARCHAR(100) | NOT NULL | 工程名（受付、入力等） |
| process_order | INT | | 工程順序（1,2,3...） |
| description | TEXT | | 工程の詳細説明 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

### 1.4 teams（チームマスタ）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| team_id | VARCHAR(20) | PK | チームID |
| team_name | VARCHAR(100) | NOT NULL | チーム名 |
| location_id | VARCHAR(10) | NOT NULL, FK | 所属拠点ID |
| team_leader_id | VARCHAR(20) | FK | チームリーダーのオペレータID |
| description | TEXT | | チームの説明 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

### 1.5 operators（オペレータマスタ）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| operator_id | VARCHAR(20) | PK | オペレータID |
| operator_name | VARCHAR(100) | NOT NULL | オペレータ名 |
| employee_no | VARCHAR(20) | UNIQUE | 従業員番号 |
| location_id | VARCHAR(10) | FK | 所属拠点ID |
| team_id | VARCHAR(20) | FK | 所属チームID |
| hired_date | DATE | | 入社日 |
| status | ENUM('active', 'inactive', 'leave') | DEFAULT 'active' | 状態（在職、退職、休職） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

## 2. バッチ2専用テーブル（配置情報取得エンジン）

### 2.1 current_assignments（現在の配置情報）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| assignment_id | INT | PK, AUTO_INCREMENT | 配置ID |
| operator_id | VARCHAR(20) | NOT NULL, FK | オペレータID |
| business_id | VARCHAR(20) | NOT NULL, FK | 業務ID |
| process_id | VARCHAR(20) | NOT NULL, FK | 工程ID |
| location_id | VARCHAR(10) | NOT NULL, FK | 拠点ID |
| team_id | VARCHAR(20) | | チームID |
| assigned_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 配置開始日時 |
| status | ENUM('active', 'standby', 'break') | DEFAULT 'active' | 配置状態（稼働中、待機、休憩） |

### 2.2 operator_skills（オペレータスキル情報）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| skill_id | INT | PK, AUTO_INCREMENT | スキルID |
| operator_id | VARCHAR(20) | NOT NULL, FK | オペレータID |
| business_id | VARCHAR(20) | NOT NULL, FK | 業務ID |
| process_id | VARCHAR(20) | NOT NULL, FK | 工程ID |
| skill_level | ENUM('beginner', 'intermediate', 'advanced', 'expert') | NOT NULL | スキルレベル（初級、中級、上級、エキスパート） |
| can_perform | BOOLEAN | DEFAULT TRUE | 実施可否フラグ |
| certified_date | DATE | | 認定日 |
| notes | TEXT | | 備考・特記事項 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

### 2.3 processing_status（処理状況）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| status_id | INT | PK, AUTO_INCREMENT | 処理状況ID |
| business_id | VARCHAR(20) | NOT NULL, FK | 業務ID |
| process_id | VARCHAR(20) | NOT NULL, FK | 工程ID |
| location_id | VARCHAR(10) | NOT NULL, FK | 拠点ID |
| received_count | INT | DEFAULT 0 | 受付件数 |
| completed_count | INT | DEFAULT 0 | 完了件数 |
| pending_count | INT | DEFAULT 0 | 未処理件数 |
| not_started_count | INT | DEFAULT 0 | 未着手件数 |
| recorded_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 記録日時 |

### 2.4 login_status（ログイン状況）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| login_id | INT | PK, AUTO_INCREMENT | ログインID |
| operator_id | VARCHAR(20) | NOT NULL, FK | オペレータID |
| location_id | VARCHAR(10) | NOT NULL, FK | 拠点ID |
| business_id | VARCHAR(20) | NOT NULL, FK | 業務ID |
| process_id | VARCHAR(20) | NOT NULL, FK | 工程ID |
| login_time | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | ログイン日時 |
| logout_time | TIMESTAMP | | ログアウト日時 |
| terminal_id | VARCHAR(50) | | 端末ID |
| status | ENUM('logged_in', 'logged_out') | DEFAULT 'logged_in' | ログイン状態 |

## 3. バッチ3専用テーブル（OP実績取得エンジン）

### 3.1 operator_performance（個人別実績）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| performance_id | INT | PK, AUTO_INCREMENT | 実績ID |
| operator_id | VARCHAR(20) | NOT NULL, FK | オペレータID |
| business_id | VARCHAR(20) | NOT NULL, FK | 業務ID |
| process_id | VARCHAR(20) | NOT NULL, FK | 工程ID |
| location_id | VARCHAR(10) | NOT NULL, FK | 拠点ID |
| work_date | DATE | NOT NULL | 作業日 |
| processed_count | INT | DEFAULT 0 | 処理件数 |
| input_items_count | INT | DEFAULT 0 | 入力項目数 |
| error_count | INT | DEFAULT 0 | エラー件数（ミス項目数） |
| unread_count | INT | DEFAULT 0 | 不読件数 |
| total_processing_time | INT | DEFAULT 0 | 総処理時間（秒） |
| average_processing_time | DECIMAL(10,2) | | 平均処理時間（秒） |
| quality_score | DECIMAL(5,2) | | 品質スコア（0-100） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

### 3.2 location_productivity（拠点別生産性）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| productivity_id | INT | PK, AUTO_INCREMENT | 生産性ID |
| location_id | VARCHAR(10) | NOT NULL, FK | 拠点ID |
| business_id | VARCHAR(20) | NOT NULL, FK | 業務ID |
| process_id | VARCHAR(20) | NOT NULL, FK | 工程ID |
| measured_at | TIMESTAMP | NOT NULL | 測定日時 |
| operator_count | INT | DEFAULT 0 | オペレータ数 |
| total_processed | INT | DEFAULT 0 | 総処理件数 |
| productivity_rate | DECIMAL(10,2) | | 生産性率（1人あたりの処理件数/時間） |
| utilization_rate | DECIMAL(5,2) | | 稼働率（%） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

### 3.3 workload_trends（業務量推移）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| trend_id | INT | PK, AUTO_INCREMENT | 推移ID |
| business_id | VARCHAR(20) | NOT NULL, FK | 業務ID |
| process_id | VARCHAR(20) | NOT NULL, FK | 工程ID |
| location_id | VARCHAR(10) | FK | 拠点ID（全拠点の場合はNULL） |
| measured_at | TIMESTAMP | NOT NULL | 測定日時 |
| received_count | INT | DEFAULT 0 | 受付件数 |
| completed_count | INT | DEFAULT 0 | 完了件数 |
| pending_count | INT | DEFAULT 0 | 待機件数 |
| average_wait_time | INT | | 平均待機時間（秒） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

## 4. AI学習用テーブル

### 4.1 assignment_history（配置調整履歴）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| history_id | INT | PK, AUTO_INCREMENT | 履歴ID |
| operator_id | VARCHAR(20) | NOT NULL, FK | オペレータID |
| from_business_id | VARCHAR(20) | | 変更前業務ID |
| from_process_id | VARCHAR(20) | | 変更前工程ID |
| from_location_id | VARCHAR(10) | | 変更前拠点ID |
| to_business_id | VARCHAR(20) | NOT NULL, FK | 変更後業務ID |
| to_process_id | VARCHAR(20) | NOT NULL, FK | 変更後工程ID |
| to_location_id | VARCHAR(10) | NOT NULL, FK | 変更後拠点ID |
| reassigned_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 配置変更日時 |
| reassigned_by | VARCHAR(50) | | 変更実行者（管理者IDまたは'AI'） |
| reason | TEXT | | 変更理由 |
| result_evaluation | ENUM('success', 'failure', 'neutral') | | 結果評価（成功、失敗、中立） |
| productivity_impact | DECIMAL(5,2) | | 生産性への影響（%） |
| notes | TEXT | | 備考 |

### 4.2 manager_decisions（管理者判断ログ）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| decision_id | INT | PK, AUTO_INCREMENT | 判断ID |
| decision_type | ENUM('assignment', 'rejection', 'modification') | NOT NULL | 判断タイプ（承認、却下、修正） |
| ai_suggestion_id | VARCHAR(50) | | AI提案ID |
| manager_id | VARCHAR(50) | NOT NULL | 管理者ID |
| decision_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 判断日時 |
| context | JSON | | 判断時の状況（JSON形式） |
| decision_reason | TEXT | | 判断理由 |
| affected_operators | JSON | | 影響を受けたオペレータのリスト |
| business_impact | TEXT | | 業務への影響 |
| learned_pattern | TEXT | | AIが学習すべきパターン |

### 4.3 ai_suggestions（AI提案履歴）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| suggestion_id | VARCHAR(50) | PK | AI提案ID |
| suggested_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 提案日時 |
| suggestion_type | ENUM('reassignment', 'optimization', 'alert') | NOT NULL | 提案タイプ（配置変更、最適化、アラート） |
| priority | ENUM('low', 'medium', 'high', 'critical') | DEFAULT 'medium' | 優先度 |
| suggestion_details | JSON | | 提案の詳細（JSON形式） |
| confidence_score | DECIMAL(3,2) | | 信頼度スコア（0-1） |
| status | ENUM('pending', 'approved', 'rejected', 'modified') | DEFAULT 'pending' | ステータス |
| approved_by | VARCHAR(50) | | 承認者 |
| approved_at | TIMESTAMP | | 承認日時 |
| feedback | TEXT | | フィードバック |

### 4.4 knowledge_embeddings（知識ベクトル）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| embedding_id | INT | PK, AUTO_INCREMENT | 埋め込みID |
| source_type | ENUM('decision', 'pattern', 'rule', 'case') | NOT NULL | ソースタイプ（判断、パターン、ルール、事例） |
| source_id | VARCHAR(50) | NOT NULL | ソースID |
| content | TEXT | NOT NULL | 元テキスト内容 |
| embedding_vector | JSON | | ベクトル化されたデータ |
| metadata | JSON | | メタデータ |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

## 5. システム連携テーブル

### 5.1 data_imports（データインポート履歴）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| import_id | INT | PK, AUTO_INCREMENT | インポートID |
| file_name | VARCHAR(255) | NOT NULL | ファイル名 |
| file_type | ENUM('RWLOGIN', 'RWLOGIN_LOCATION', 'FS', 'RWMSGCOUNT', 'NOTINPUT', 'OPERATOR_PERFORMANCE') | NOT NULL | ファイルタイプ |
| import_status | ENUM('pending', 'processing', 'completed', 'failed') | DEFAULT 'pending' | インポート状況 |
| record_count | INT | DEFAULT 0 | レコード数 |
| error_count | INT | DEFAULT 0 | エラー数 |
| error_details | JSON | | エラー詳細 |
| imported_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | インポート開始日時 |
| completed_at | TIMESTAMP | | インポート完了日時 |

### 5.2 system_notifications（システム通知）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| notification_id | INT | PK, AUTO_INCREMENT | 通知ID |
| notification_type | ENUM('reassignment', 'alert', 'deadline', 'system') | NOT NULL | 通知タイプ |
| recipient_type | ENUM('operator', 'manager', 'system') | NOT NULL | 受信者タイプ |
| recipient_id | VARCHAR(20) | | 受信者ID |
| title | VARCHAR(255) | NOT NULL | 通知タイトル |
| message | TEXT | NOT NULL | 通知メッセージ |
| priority | ENUM('low', 'medium', 'high', 'urgent') | DEFAULT 'medium' | 優先度 |
| status | ENUM('pending', 'sent', 'read', 'acknowledged') | DEFAULT 'pending' | 通知状況 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| sent_at | TIMESTAMP | | 送信日時 |
| read_at | TIMESTAMP | | 既読日時 |

## 6. UI設定テーブル

### 6.1 ui_dashboards（ダッシュボード設定）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| dashboard_id | INT | PK, AUTO_INCREMENT | ダッシュボードID |
| user_id | VARCHAR(20) | NOT NULL | ユーザーID |
| dashboard_name | VARCHAR(100) | NOT NULL | ダッシュボード名 |
| layout_config | JSON | | レイアウト設定 |
| widget_config | JSON | | ウィジェット設定 |
| is_default | BOOLEAN | DEFAULT FALSE | デフォルトフラグ |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

### 6.2 ui_preferences（ユーザー設定）
| カラム名 | データ型 | 制約 | 説明 |
|----------|---------|------|------|
| preference_id | INT | PK, AUTO_INCREMENT | 設定ID |
| user_id | VARCHAR(20) | NOT NULL, UNIQUE | ユーザーID |
| theme | ENUM('light', 'dark', 'auto') | DEFAULT 'light' | テーマ設定 |
| language | VARCHAR(10) | DEFAULT 'ja' | 言語設定 |
| notification_settings | JSON | | 通知設定 |
| display_settings | JSON | | 表示設定 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

## 7. インデックス一覧

### 主要インデックス
| テーブル名 | インデックス名 | 対象カラム | 用途 |
|-----------|---------------|------------|------|
| operators | idx_status | status | ステータス検索 |
| operators | idx_location_team | location_id, team_id | 拠点・チーム別検索 |
| current_assignments | idx_operator_status | operator_id, status | オペレータ別状況検索 |
| current_assignments | idx_location_process | location_id, process_id | 拠点・工程別検索 |
| operator_performance | idx_operator_date | operator_id, work_date | オペレータ別日付検索 |
| operator_performance | idx_location_date | location_id, work_date | 拠点別日付検索 |
| login_status | idx_operator_status | operator_id, status | ログイン状況検索 |
| login_status | idx_login_time | login_time | ログイン時刻検索 |
| processing_status | idx_recorded_at | recorded_at | 記録時刻検索 |
| assignment_history | idx_reassigned_at | reassigned_at | 配置変更時刻検索 |
| assignment_history | idx_operator | operator_id | オペレータ別履歴検索 |
| manager_decisions | idx_decision_at | decision_at | 判断時刻検索 |
| ai_suggestions | idx_suggested_at | suggested_at | 提案時刻検索 |
| ai_suggestions | idx_status | status | 提案状況検索 |
| system_notifications | idx_recipient | recipient_id, status | 受信者別通知検索 |

## 8. 制約一覧

### 外部キー制約
| 子テーブル | 子カラム | 親テーブル | 親カラム |
|-----------|---------|-----------|---------|
| processes | business_id | business_types | business_id |
| teams | location_id | locations | location_id |
| teams | team_leader_id | operators | operator_id |
| operators | location_id | locations | location_id |
| operators | team_id | teams | team_id |
| current_assignments | operator_id | operators | operator_id |
| current_assignments | business_id | business_types | business_id |
| current_assignments | process_id | processes | process_id |
| current_assignments | location_id | locations | location_id |
| operator_skills | operator_id | operators | operator_id |
| operator_skills | business_id | business_types | business_id |
| operator_skills | process_id | processes | process_id |
| processing_status | business_id | business_types | business_id |
| processing_status | process_id | processes | process_id |
| processing_status | location_id | locations | location_id |
| login_status | operator_id | operators | operator_id |
| login_status | location_id | locations | location_id |
| login_status | business_id | business_types | business_id |
| login_status | process_id | processes | process_id |

### ユニーク制約
| テーブル名 | 制約名 | 対象カラム |
|-----------|-------|-----------|
| operators | employee_no | employee_no |
| operator_skills | unique_operator_skill | operator_id, business_id, process_id |
| ui_preferences | user_id | user_id |