-- AIエージェント（Aimee）データベース初期化スクリプト

-- データベース作成（必要に応じて）
-- CREATE DATABASE aimee_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE aimee_db;

-- 既存テーブルの削除（開発環境用）
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS knowledge_embeddings;
DROP TABLE IF EXISTS ai_suggestions;
DROP TABLE IF EXISTS manager_decisions;
DROP TABLE IF EXISTS assignment_history;
DROP TABLE IF EXISTS workload_trends;
DROP TABLE IF EXISTS location_productivity;
DROP TABLE IF EXISTS operator_performance;
DROP TABLE IF EXISTS login_status;
DROP TABLE IF EXISTS processing_status;
DROP TABLE IF EXISTS operator_skills;
DROP TABLE IF EXISTS current_assignments;
DROP TABLE IF EXISTS operators;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS processes;
DROP TABLE IF EXISTS business_types;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS data_imports;
DROP TABLE IF EXISTS system_notifications;
DROP TABLE IF EXISTS ui_dashboards;
DROP TABLE IF EXISTS ui_preferences;
SET FOREIGN_KEY_CHECKS = 1;

-- ========================
-- 共通マスタテーブル
-- ========================

-- 1. locations（拠点マスタ）
CREATE TABLE locations (
    location_id VARCHAR(10) PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. business_types（業務マスタ）
CREATE TABLE business_types (
    business_id VARCHAR(20) PRIMARY KEY,
    business_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. processes（工程マスタ）
CREATE TABLE processes (
    process_id VARCHAR(20) PRIMARY KEY,
    business_id VARCHAR(20) NOT NULL,
    process_name VARCHAR(100) NOT NULL,
    process_order INT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES business_types(business_id),
    INDEX idx_business_id (business_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. teams（チームマスタ）
CREATE TABLE teams (
    team_id VARCHAR(20) PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    location_id VARCHAR(10) NOT NULL,
    team_leader_id VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_location_id (location_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. operators（オペレータマスタ）
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
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    INDEX idx_status (status),
    INDEX idx_location_team (location_id, team_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- teamsテーブルに外部キー制約を追加（team_leader_id）
ALTER TABLE teams ADD FOREIGN KEY (team_leader_id) REFERENCES operators(operator_id);

-- ========================
-- バッチ2専用テーブル
-- ========================

-- 6. current_assignments（現在の配置情報）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. operator_skills（オペレータスキル情報）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. processing_status（処理状況）
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
    INDEX idx_recorded_at (recorded_at),
    INDEX idx_location_process (location_id, process_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. login_status（ログイン状況）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================
-- バッチ3専用テーブル
-- ========================

-- 10. operator_performance（個人別実績）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. location_productivity（拠点別生産性）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. workload_trends（業務量推移）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================
-- AI学習用テーブル
-- ========================

-- 13. assignment_history（配置調整履歴）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 14. manager_decisions（管理者判断ログ）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 15. ai_suggestions（AI提案履歴）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 16. knowledge_embeddings（知識ベクトル）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================
-- システム連携テーブル
-- ========================

-- 17. data_imports（データインポート履歴）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 18. system_notifications（システム通知）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================
-- UI設定テーブル
-- ========================

-- 19. ui_dashboards（ダッシュボード設定）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 20. ui_preferences（ユーザー設定）
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================
-- 初期データ投入
-- ========================

-- 拠点マスタの初期データ
INSERT INTO locations (location_id, location_name, region) VALUES
('LOC001', '札幌センター', '北海道'),
('LOC002', '仙台センター', '東北'),
('LOC003', '東京センター', '関東'),
('LOC004', '名古屋センター', '中部'),
('LOC005', '大阪センター', '関西'),
('LOC006', '広島センター', '中国'),
('LOC007', '福岡センター', '九州'),
('LOC008', '那覇センター', '沖縄'),
('LOC009', '新潟センター', '北陸');

-- 業務マスタの初期データ
INSERT INTO business_types (business_id, business_name, description) VALUES
('BUS001', '健康保険申請', '健康保険に関する各種申請業務'),
('BUS002', '給付金処理', '各種給付金の申請・支払い処理'),
('BUS003', '資格確認', '被保険者資格の確認・更新業務');

-- 工程マスタの初期データ
INSERT INTO processes (process_id, business_id, process_name, process_order) VALUES
('PROC001', 'BUS001', '受付', 1),
('PROC002', 'BUS001', '入力', 2),
('PROC003', 'BUS001', '審査', 3),
('PROC004', 'BUS001', '承認', 4),
('PROC005', 'BUS001', '納品', 5),
('PROC006', 'BUS002', '受付', 1),
('PROC007', 'BUS002', '審査', 2),
('PROC008', 'BUS002', '支払処理', 3),
('PROC009', 'BUS003', '申請受付', 1),
('PROC010', 'BUS003', '確認作業', 2);

-- ========================
-- ビュー作成（オプション）
-- ========================

-- 現在の配置状況ビュー
CREATE VIEW v_current_allocation AS
SELECT 
    ca.assignment_id,
    o.operator_id,
    o.operator_name,
    o.employee_no,
    l.location_name,
    t.team_name,
    bt.business_name,
    p.process_name,
    ca.status,
    ca.assigned_at
FROM current_assignments ca
JOIN operators o ON ca.operator_id = o.operator_id
JOIN locations l ON ca.location_id = l.location_id
LEFT JOIN teams t ON o.team_id = t.team_id
JOIN business_types bt ON ca.business_id = bt.business_id
JOIN processes p ON ca.process_id = p.process_id
WHERE ca.status = 'active';

-- オペレータスキルサマリビュー
CREATE VIEW v_operator_skills_summary AS
SELECT 
    o.operator_id,
    o.operator_name,
    COUNT(DISTINCT os.business_id) as business_count,
    COUNT(DISTINCT os.process_id) as process_count,
    GROUP_CONCAT(DISTINCT bt.business_name) as businesses,
    MAX(os.skill_level) as max_skill_level
FROM operators o
LEFT JOIN operator_skills os ON o.operator_id = os.operator_id
LEFT JOIN business_types bt ON os.business_id = bt.business_id
WHERE os.can_perform = TRUE
GROUP BY o.operator_id, o.operator_name;

-- ========================
-- ストアドプロシージャ（オプション）
-- ========================

DELIMITER $$

-- 配置変更記録プロシージャ
CREATE PROCEDURE sp_record_assignment_change(
    IN p_operator_id VARCHAR(20),
    IN p_from_business_id VARCHAR(20),
    IN p_from_process_id VARCHAR(20),
    IN p_from_location_id VARCHAR(10),
    IN p_to_business_id VARCHAR(20),
    IN p_to_process_id VARCHAR(20),
    IN p_to_location_id VARCHAR(10),
    IN p_reassigned_by VARCHAR(50),
    IN p_reason TEXT
)
BEGIN
    -- トランザクション開始
    START TRANSACTION;
    
    -- 現在の配置を無効化
    UPDATE current_assignments
    SET status = 'inactive'
    WHERE operator_id = p_operator_id AND status = 'active';
    
    -- 新しい配置を作成
    INSERT INTO current_assignments (
        operator_id, business_id, process_id, location_id, status
    ) VALUES (
        p_operator_id, p_to_business_id, p_to_process_id, p_to_location_id, 'active'
    );
    
    -- 履歴に記録
    INSERT INTO assignment_history (
        operator_id, 
        from_business_id, from_process_id, from_location_id,
        to_business_id, to_process_id, to_location_id,
        reassigned_by, reason
    ) VALUES (
        p_operator_id,
        p_from_business_id, p_from_process_id, p_from_location_id,
        p_to_business_id, p_to_process_id, p_to_location_id,
        p_reassigned_by, p_reason
    );
    
    COMMIT;
END$$

DELIMITER ;

-- ========================
-- 権限設定（本番環境用）
-- ========================

-- アプリケーションユーザー作成（例）
-- CREATE USER 'aimee_app'@'localhost' IDENTIFIED BY 'secure_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON aimee_db.* TO 'aimee_app'@'localhost';
-- GRANT EXECUTE ON aimee_db.* TO 'aimee_app'@'localhost';

-- 読み取り専用ユーザー作成（例）
-- CREATE USER 'aimee_readonly'@'localhost' IDENTIFIED BY 'secure_password';
-- GRANT SELECT ON aimee_db.* TO 'aimee_readonly'@'localhost';

-- FLUSH PRIVILEGES;