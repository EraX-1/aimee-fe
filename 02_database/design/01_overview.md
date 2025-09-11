# AIエージェント（Aimee）データベース設計

## 概要
このデータベース設計は、バッチ2（配置情報取得エンジン）とバッチ3（OP実績取得エンジン）の両方のニーズを満たすように設計されています。

## テーブル設計

### 共通マスタテーブル

#### 1. locations（拠点マスタ）
```sql
CREATE TABLE locations (
    location_id VARCHAR(10) PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 2. business_types（業務マスタ）
```sql
CREATE TABLE business_types (
    business_id VARCHAR(20) PRIMARY KEY,
    business_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 3. processes（工程マスタ）
```sql
CREATE TABLE processes (
    process_id VARCHAR(20) PRIMARY KEY,
    business_id VARCHAR(20) NOT NULL,
    process_name VARCHAR(100) NOT NULL,
    process_order INT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES business_types(business_id)
);
```

#### 4. operators（オペレータマスタ）
```sql
CREATE TABLE operators (
    operator_id VARCHAR(20) PRIMARY KEY,
    operator_name VARCHAR(100) NOT NULL,
    employee_no VARCHAR(20) UNIQUE,
    location_id VARCHAR(10),
    team_id VARCHAR(20),
    hired_date DATE,
    status ENUM('active', 'inactive', 'leave') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);
```

#### 5. teams（チームマスタ）
```sql
CREATE TABLE teams (
    team_id VARCHAR(20) PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    location_id VARCHAR(10) NOT NULL,
    team_leader_id VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (team_leader_id) REFERENCES operators(operator_id)
);
```

### バッチ2専用テーブル（配置情報取得エンジン）

#### 6. current_assignments（現在の配置情報）
```sql
CREATE TABLE current_assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    operator_id VARCHAR(20) NOT NULL,
    business_id VARCHAR(20) NOT NULL,
    process_id VARCHAR(20) NOT NULL,
    location_id VARCHAR(10) NOT NULL,
    team_id VARCHAR(20),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('active', 'standby', 'break') DEFAULT 'active',
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id),
    FOREIGN KEY (business_id) REFERENCES business_types(business_id),
    FOREIGN KEY (process_id) REFERENCES processes(process_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_operator_status (operator_id, status),
    INDEX idx_location_process (location_id, process_id)
);
```

#### 7. operator_skills（オペレータスキル情報）
```sql
CREATE TABLE operator_skills (
    skill_id INT PRIMARY KEY AUTO_INCREMENT,
    operator_id VARCHAR(20) NOT NULL,
    business_id VARCHAR(20) NOT NULL,
    process_id VARCHAR(20) NOT NULL,
    skill_level ENUM('beginner', 'intermediate', 'advanced', 'expert') NOT NULL,
    can_perform BOOLEAN DEFAULT TRUE,
    certified_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id),
    FOREIGN KEY (business_id) REFERENCES business_types(business_id),
    FOREIGN KEY (process_id) REFERENCES processes(process_id),
    UNIQUE KEY unique_operator_skill (operator_id, business_id, process_id)
);
```

#### 8. processing_status（処理状況）
```sql
CREATE TABLE processing_status (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    business_id VARCHAR(20) NOT NULL,
    process_id VARCHAR(20) NOT NULL,
    location_id VARCHAR(10) NOT NULL,
    received_count INT DEFAULT 0,
    completed_count INT DEFAULT 0,
    pending_count INT DEFAULT 0,
    not_started_count INT DEFAULT 0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES business_types(business_id),
    FOREIGN KEY (process_id) REFERENCES processes(process_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_recorded_at (recorded_at)
);
```

#### 9. login_status（ログイン状況）
```sql
CREATE TABLE login_status (
    login_id INT PRIMARY KEY AUTO_INCREMENT,
    operator_id VARCHAR(20) NOT NULL,
    location_id VARCHAR(10) NOT NULL,
    business_id VARCHAR(20) NOT NULL,
    process_id VARCHAR(20) NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,
    terminal_id VARCHAR(50),
    status ENUM('logged_in', 'logged_out') DEFAULT 'logged_in',
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (business_id) REFERENCES business_types(business_id),
    FOREIGN KEY (process_id) REFERENCES processes(process_id),
    INDEX idx_operator_status (operator_id, status),
    INDEX idx_login_time (login_time)
);
```

### バッチ3専用テーブル（OP実績取得エンジン）

#### 10. operator_performance（個人別実績）
```sql
CREATE TABLE operator_performance (
    performance_id INT PRIMARY KEY AUTO_INCREMENT,
    operator_id VARCHAR(20) NOT NULL,
    business_id VARCHAR(20) NOT NULL,
    process_id VARCHAR(20) NOT NULL,
    location_id VARCHAR(10) NOT NULL,
    work_date DATE NOT NULL,
    processed_count INT DEFAULT 0,
    input_items_count INT DEFAULT 0,
    error_count INT DEFAULT 0,
    unread_count INT DEFAULT 0,
    total_processing_time INT DEFAULT 0, -- 秒単位
    average_processing_time DECIMAL(10,2), -- 秒単位
    quality_score DECIMAL(5,2), -- 品質スコア（0-100）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id),
    FOREIGN KEY (business_id) REFERENCES business_types(business_id),
    FOREIGN KEY (process_id) REFERENCES processes(process_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_operator_date (operator_id, work_date),
    INDEX idx_location_date (location_id, work_date)
);
```

#### 11. location_productivity（拠点別生産性）
```sql
CREATE TABLE location_productivity (
    productivity_id INT PRIMARY KEY AUTO_INCREMENT,
    location_id VARCHAR(10) NOT NULL,
    business_id VARCHAR(20) NOT NULL,
    process_id VARCHAR(20) NOT NULL,
    measured_at TIMESTAMP NOT NULL,
    operator_count INT DEFAULT 0,
    total_processed INT DEFAULT 0,
    productivity_rate DECIMAL(10,2), -- 1人あたりの処理件数/時間
    utilization_rate DECIMAL(5,2), -- 稼働率（%）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (business_id) REFERENCES business_types(business_id),
    FOREIGN KEY (process_id) REFERENCES processes(process_id),
    INDEX idx_measured_at (measured_at),
    INDEX idx_location_time (location_id, measured_at)
);
```

#### 12. workload_trends（業務量推移）
```sql
CREATE TABLE workload_trends (
    trend_id INT PRIMARY KEY AUTO_INCREMENT,
    business_id VARCHAR(20) NOT NULL,
    process_id VARCHAR(20) NOT NULL,
    location_id VARCHAR(10),
    measured_at TIMESTAMP NOT NULL,
    received_count INT DEFAULT 0,
    completed_count INT DEFAULT 0,
    pending_count INT DEFAULT 0,
    average_wait_time INT, -- 秒単位
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES business_types(business_id),
    FOREIGN KEY (process_id) REFERENCES processes(process_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_measured_at (measured_at),
    INDEX idx_business_time (business_id, measured_at)
);
```

### AI学習用テーブル（両バッチで使用）

#### 13. assignment_history（配置調整履歴）
```sql
CREATE TABLE assignment_history (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    operator_id VARCHAR(20) NOT NULL,
    from_business_id VARCHAR(20),
    from_process_id VARCHAR(20),
    from_location_id VARCHAR(10),
    to_business_id VARCHAR(20) NOT NULL,
    to_process_id VARCHAR(20) NOT NULL,
    to_location_id VARCHAR(10) NOT NULL,
    reassigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reassigned_by VARCHAR(50), -- 管理者ID or 'AI'
    reason TEXT,
    result_evaluation ENUM('success', 'failure', 'neutral'),
    productivity_impact DECIMAL(5,2), -- 生産性への影響（%）
    notes TEXT,
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id),
    FOREIGN KEY (to_business_id) REFERENCES business_types(business_id),
    FOREIGN KEY (to_process_id) REFERENCES processes(process_id),
    FOREIGN KEY (to_location_id) REFERENCES locations(location_id),
    INDEX idx_reassigned_at (reassigned_at),
    INDEX idx_operator (operator_id)
);
```

#### 14. manager_decisions（管理者判断ログ）
```sql
CREATE TABLE manager_decisions (
    decision_id INT PRIMARY KEY AUTO_INCREMENT,
    decision_type ENUM('assignment', 'rejection', 'modification') NOT NULL,
    ai_suggestion_id VARCHAR(50), -- AI提案のID
    manager_id VARCHAR(50) NOT NULL,
    decision_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context JSON, -- 判断時の状況（JSON形式）
    decision_reason TEXT,
    affected_operators JSON, -- 影響を受けたオペレータのリスト
    business_impact TEXT,
    learned_pattern TEXT, -- AIが学習すべきパターン
    INDEX idx_decision_at (decision_at),
    INDEX idx_decision_type (decision_type)
);
```

#### 15. ai_suggestions（AI提案履歴）
```sql
CREATE TABLE ai_suggestions (
    suggestion_id VARCHAR(50) PRIMARY KEY,
    suggested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    suggestion_type ENUM('reassignment', 'optimization', 'alert') NOT NULL,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    suggestion_details JSON, -- 提案の詳細（JSON形式）
    confidence_score DECIMAL(3,2), -- 信頼度スコア（0-1）
    status ENUM('pending', 'approved', 'rejected', 'modified') DEFAULT 'pending',
    approved_by VARCHAR(50),
    approved_at TIMESTAMP NULL,
    feedback TEXT,
    INDEX idx_suggested_at (suggested_at),
    INDEX idx_status (status)
);
```

### RAG用ベクトルデータテーブル

#### 16. knowledge_embeddings（知識ベクトル）
```sql
CREATE TABLE knowledge_embeddings (
    embedding_id INT PRIMARY KEY AUTO_INCREMENT,
    source_type ENUM('decision', 'pattern', 'rule', 'case') NOT NULL,
    source_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding_vector JSON, -- ベクトル化されたデータ
    metadata JSON, -- メタデータ
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_source (source_type, source_id),
    INDEX idx_created_at (created_at)
);
```

### システム連携テーブル

#### 17. data_imports（データインポート履歴）
```sql
CREATE TABLE data_imports (
    import_id INT PRIMARY KEY AUTO_INCREMENT,
    file_name VARCHAR(255) NOT NULL,
    file_type ENUM('RWLOGIN', 'RWLOGIN_LOCATION', 'FS', 'RWMSGCOUNT', 'NOTINPUT', 'OPERATOR_PERFORMANCE') NOT NULL,
    import_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    record_count INT DEFAULT 0,
    error_count INT DEFAULT 0,
    error_details JSON,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    INDEX idx_imported_at (imported_at),
    INDEX idx_status (import_status)
);
```

#### 18. system_notifications（システム通知）
```sql
CREATE TABLE system_notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    notification_type ENUM('reassignment', 'alert', 'deadline', 'system') NOT NULL,
    recipient_type ENUM('operator', 'manager', 'system') NOT NULL,
    recipient_id VARCHAR(20),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('pending', 'sent', 'read', 'acknowledged') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP NULL,
    read_at TIMESTAMP NULL,
    INDEX idx_recipient (recipient_id, status),
    INDEX idx_created_at (created_at)
);
```

### UI設定テーブル

#### 19. ui_dashboards（ダッシュボード設定）
```sql
CREATE TABLE ui_dashboards (
    dashboard_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(20) NOT NULL,
    dashboard_name VARCHAR(100) NOT NULL,
    layout_config JSON, -- レイアウト設定
    widget_config JSON, -- ウィジェット設定
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

#### 20. ui_preferences（ユーザー設定）
```sql
CREATE TABLE ui_preferences (
    preference_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(20) NOT NULL UNIQUE,
    theme ENUM('light', 'dark', 'auto') DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'ja',
    notification_settings JSON,
    display_settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

## インデックス戦略

1. **時系列データ**: measured_at, recorded_at などの時刻カラムにインデックス
2. **頻繁な検索条件**: operator_id, location_id, business_id, process_id の組み合わせ
3. **ステータス検索**: status カラムへのインデックス
4. **パーティショニング**: 大量データが予想されるテーブルは日付でパーティショニング

## データ保持ポリシー

1. **マスタデータ**: 無期限保持
2. **トランザクションデータ**: 
   - login_status: 3ヶ月
   - processing_status: 6ヶ月
   - workload_trends: 1年
   - system_notifications: 6ヶ月
3. **実績データ**: 2年
4. **AI学習データ**: 無期限保持（学習の質向上のため）
5. **システム連携データ**:
   - data_imports: 1年
6. **UI設定データ**: 無期限保持

## 技術スタック（議事録より）

### データ収集・バッチ処理
- スケジューラー: Apache Airflow / Prefect
- CSVデータ処理: pandas, polars
- データ検証: Great Expectations, pandera

### データベース・ストレージ
- RDB: PostgreSQL + SQLAlchemy + psycopg2
- 時系列データ: TimescaleDB
- 接続プール: SQLAlchemy pool
- マイグレーション: Alembic

### AIエンジン（RAG + LLM）
- ベクトルDB: ChromaDB / Qdrant / Weaviate
- 埋め込みモデル: sentence-transformers, OpenAI Embeddings
- LLMフレームワーク: LangChain / LlamaIndex
- ローカルLLM: Ollama + llama-cpp-python
- プロンプト管理: LangSmith / PromptLayer

### 最適化エンジン
- 数理最適化: PuLP, OR-Tools, scipy.optimize
- 機械学習: scikit-learn, XGBoost, LightGBM
- 深層学習: PyTorch / TensorFlow（必要に応じて）

### Web・API
- Webフレームワーク: FastAPI / Django REST Framework
- WebSocket: python-socketio
- 認証: python-jose (JWT), passlib

### UI（チャットインターフェース）
- バックエンド: FastAPI + WebSocket
- フロントエンド: Streamlit（Python）