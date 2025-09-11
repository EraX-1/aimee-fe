# データベースER図

## 全体テーブル関係図

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   locations     │     │ business_types  │     │    processes    │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ location_id (PK)│     │business_id (PK) │     │process_id (PK)  │
│ location_name   │     │business_name    │     │business_id (FK) │──┐
│ region          │     │description      │     │process_name     │  │
│ created_at      │     │created_at       │     │process_order    │  │
│ updated_at      │     │updated_at       │     │description      │  │
└────────┬────────┘     └────────┬────────┘     │created_at       │  │
         │                       │               │updated_at       │  │
         │                       │               └─────────────────┘  │
         │                       └────────────────────────────────────┘
         │
         ├─────────────┐
         │             │
┌────────▼────────┐    │    ┌─────────────────┐
│     teams       │    │    │   operators     │
├─────────────────┤    │    ├─────────────────┤
│ team_id (PK)    │    │    │operator_id (PK) │
│ team_name       │    │    │operator_name    │
│ location_id (FK)│◄───┴────┤employee_no (UK) │
│ team_leader_id  │         │location_id (FK) │
│ description     │◄────────┤team_id (FK)     │
│ created_at      │         │hired_date       │
│ updated_at      │         │status           │
└─────────────────┘         │created_at       │
                            │updated_at       │
                            └────────┬────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         │                           │                           │
┌────────▼────────┐         ┌───────▼────────┐        ┌────────▼────────┐
│current_assignments│        │operator_skills │        │  login_status   │
├─────────────────┤         ├────────────────┤        ├─────────────────┤
│assignment_id(PK)│         │skill_id (PK)   │        │login_id (PK)    │
│operator_id (FK) │         │operator_id (FK)│        │operator_id (FK) │
│business_id (FK) │         │business_id (FK)│        │location_id (FK) │
│process_id (FK)  │         │process_id (FK) │        │business_id (FK) │
│location_id (FK) │         │skill_level     │        │process_id (FK)  │
│team_id          │         │can_perform     │        │login_time       │
│assigned_at      │         │certified_date  │        │logout_time      │
│status           │         │notes           │        │terminal_id      │
└─────────────────┘         │created_at      │        │status           │
                            │updated_at      │        └─────────────────┘
                            └────────────────┘
```

## バッチ2専用テーブル関係

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         バッチ2（配置情報取得エンジン）                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────┐    ┌──────────────────┐    ┌───────────────────┐  │
│  │current_assignments│    │processing_status │    │   login_status    │  │
│  └───────────────┘    └──────────────────┘    └───────────────────┘  │
│           │                      │                         │            │
│           │                      │                         │            │
│           └──────────────────────┴─────────────────────────┘            │
│                                  │                                      │
│                          ┌───────▼────────┐                            │
│                          │operator_skills │                            │
│                          └────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

## バッチ3専用テーブル関係

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          バッチ3（OP実績取得エンジン）                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────┐  ┌─────────────────────┐  ┌─────────────────┐│
│  │operator_performance │  │location_productivity│  │workload_trends  ││
│  ├────────────────────┤  ├─────────────────────┤  ├─────────────────┤│
│  │performance_id (PK) │  │productivity_id (PK) │  │trend_id (PK)    ││
│  │operator_id (FK)    │  │location_id (FK)     │  │business_id (FK) ││
│  │business_id (FK)    │  │business_id (FK)     │  │process_id (FK)  ││
│  │process_id (FK)     │  │process_id (FK)      │  │location_id (FK) ││
│  │location_id (FK)    │  │measured_at          │  │measured_at      ││
│  │work_date           │  │operator_count       │  │received_count   ││
│  │processed_count     │  │total_processed      │  │completed_count  ││
│  │input_items_count   │  │productivity_rate    │  │pending_count    ││
│  │error_count         │  │utilization_rate     │  │average_wait_time││
│  │unread_count        │  │created_at           │  │created_at       ││
│  │total_processing_time│  └─────────────────────┘  └─────────────────┘│
│  │average_processing_time│                                              │
│  │quality_score       │                                                │
│  │created_at          │                                                │
│  └────────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

## AI学習・システム連携テーブル

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AI学習・システム連携                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐     ┌─────────────────┐    ┌─────────────────┐ │
│  │assignment_history │     │manager_decisions│    │ ai_suggestions  │ │
│  ├──────────────────┤     ├─────────────────┤    ├─────────────────┤ │
│  │history_id (PK)   │     │decision_id (PK) │◄───┤suggestion_id(PK)│ │
│  │operator_id (FK)  │     │decision_type    │    │suggested_at     │ │
│  │from_business_id  │     │ai_suggestion_id │    │suggestion_type  │ │
│  │from_process_id   │     │manager_id       │    │priority         │ │
│  │from_location_id  │     │decision_at      │    │suggestion_details│ │
│  │to_business_id    │     │context (JSON)   │    │confidence_score │ │
│  │to_process_id     │     │decision_reason  │    │status           │ │
│  │to_location_id    │     │affected_operators│   │approved_by      │ │
│  │reassigned_at     │     │business_impact  │    │approved_at      │ │
│  │reassigned_by     │     │learned_pattern  │    │feedback         │ │
│  │reason            │     └────────┬────────┘    └─────────────────┘ │
│  │result_evaluation │              │                                  │
│  │productivity_impact│             │                                  │
│  │notes             │              ▼                                  │
│  └──────────┬───────┘     ┌────────────────────┐                     │
│             │             │knowledge_embeddings │                     │
│             └────────────►├────────────────────┤                     │
│                           │embedding_id (PK)   │                     │
│                           │source_type         │                     │
│                           │source_id           │                     │
│                           │content             │                     │
│                           │embedding_vector    │                     │
│                           │metadata (JSON)     │                     │
│                           │created_at          │                     │
│                           │updated_at          │                     │
│                           └────────────────────┘                     │
│                                                                       │
│  ┌──────────────────┐     ┌───────────────────────┐                 │
│  │  data_imports    │     │ system_notifications  │                 │
│  ├──────────────────┤     ├───────────────────────┤                 │
│  │import_id (PK)    │     │notification_id (PK)   │                 │
│  │file_name         │     │notification_type      │                 │
│  │file_type         │     │recipient_type         │                 │
│  │import_status     │     │recipient_id           │                 │
│  │record_count      │     │title                  │                 │
│  │error_count       │     │message                │                 │
│  │error_details     │     │priority               │                 │
│  │imported_at       │     │status                 │                 │
│  │completed_at      │     │created_at             │                 │
│  └──────────────────┘     │sent_at                │                 │
│                           │read_at                │                 │
│                           └───────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
```

## UI設定テーブル

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              UI設定関連                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│         ┌──────────────────┐           ┌──────────────────┐           │
│         │  ui_dashboards    │           │  ui_preferences   │           │
│         ├──────────────────┤           ├──────────────────┤           │
│         │dashboard_id (PK)  │           │preference_id (PK) │           │
│         │user_id           │           │user_id (UK)       │           │
│         │dashboard_name     │           │theme              │           │
│         │layout_config(JSON)│           │language           │           │
│         │widget_config(JSON)│           │notification_settings│         │
│         │is_default         │           │display_settings   │           │
│         │created_at         │           │created_at         │           │
│         │updated_at         │           │updated_at         │           │
│         └──────────────────┘           └──────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

## 主要な関係性

### 1. オペレータ中心の関係
- operators → locations (所属拠点)
- operators → teams (所属チーム)
- operators → current_assignments (現在の配置)
- operators → operator_skills (スキル情報)
- operators → login_status (ログイン状態)
- operators → operator_performance (実績)

### 2. 業務・工程の階層
- business_types → processes (1:N)
- 各テーブルが business_id, process_id を持つことで業務・工程を特定

### 3. 配置最適化の流れ
1. current_assignments (現在配置) + operator_skills (スキル)
2. → ai_suggestions (AI提案)
3. → manager_decisions (管理者判断)
4. → assignment_history (配置変更履歴)
5. → knowledge_embeddings (学習データ化)

### 4. データフロー
- CSVファイル → data_imports → 各業務テーブル
- 実績データ → operator_performance → location_productivity
- リアルタイムデータ → processing_status, workload_trends

## インデックス設計

### 主キー・外部キー
- 全テーブルに主キー設定
- 外部キーには自動的にインデックス作成

### 追加インデックス
1. **時系列検索用**
   - recorded_at, measured_at, created_at, imported_at

2. **ステータス検索用**
   - status カラム全般

3. **複合インデックス**
   - (operator_id, work_date)
   - (location_id, measured_at)
   - (recipient_id, status)

## テーブル利用マトリクス

| テーブル名 | バッチ2<br>(配置情報) | バッチ3<br>(実績取得) | AI学習 | UI |
|-----------|---------------------|---------------------|--------|-----|
| **共通マスタ** |
| locations | ✓ | ✓ | ✓ | ✓ |
| business_types | ✓ | ✓ | ✓ | ✓ |
| processes | ✓ | ✓ | ✓ | ✓ |
| operators | ✓ | ✓ | ✓ | ✓ |
| teams | ✓ | ✓ | ✓ | ✓ |
| **バッチ2専用** |
| current_assignments | ✓ | - | ✓ | ✓ |
| operator_skills | ✓ | - | ✓ | ✓ |
| processing_status | ✓ | - | - | ✓ |
| login_status | ✓ | - | - | ✓ |
| **バッチ3専用** |
| operator_performance | - | ✓ | ✓ | ✓ |
| location_productivity | - | ✓ | ✓ | ✓ |
| workload_trends | - | ✓ | ✓ | ✓ |
| **AI学習用** |
| assignment_history | ✓ | ✓ | ✓ | ✓ |
| manager_decisions | ✓ | ✓ | ✓ | ✓ |
| ai_suggestions | ✓ | ✓ | ✓ | ✓ |
| knowledge_embeddings | ✓ | ✓ | ✓ | - |
| **システム連携** |
| data_imports | ✓ | ✓ | - | ✓ |
| system_notifications | ✓ | ✓ | - | ✓ |
| **UI設定** |
| ui_dashboards | - | - | - | ✓ |
| ui_preferences | - | - | - | ✓ |