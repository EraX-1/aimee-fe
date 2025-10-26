# AIMEE ドキュメントアーカイブ

このフォルダには詳細な技術資料、過去のレポート、アーキテクチャドキュメントが保管されています。

**整理日**: 2025-10-24

---

## 📚 ドキュメント分類

### アーキテクチャ・技術詳細
- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - システムアーキテクチャ詳解
- **[TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md)** - 技術スタック、パフォーマンス
- **[INTEGRATION.md](INTEGRATION.md)** - フロント・バックエンド統合ガイド

### AWS・デプロイ
- **[AWS_DEPLOY_GUIDE.md](AWS_DEPLOY_GUIDE.md)** - AWS本番環境デプロイ手順
- **[AWS_COMPLETE_GUIDE.md](AWS_COMPLETE_GUIDE.md)** - AWS完全ガイド

### デモ・テスト
- **[REAL_DATA_SUCCESS.md](REAL_DATA_SUCCESS.md)** - 実データテスト結果
- **[DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md)** - デモ動画用台本
- **[DEMO_QUESTIONS.md](DEMO_QUESTIONS.md)** - デモ用質問文パターン

### 業務・仕様
- **[BUSINESS_HIERARCHY.md](BUSINESS_HIERARCHY.md)** - 業務階層構造
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - 使い方ガイド

### 開発履歴
- **[COMPLETE.md](COMPLETE.md)** - 完了作業記録
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - 実装状況まとめ
- **[IMPLEMENTATION_STATUS_GOOGLE_DOCS.md](IMPLEMENTATION_STATUS_GOOGLE_DOCS.md)** - Google Docs版実装状況
- **[MOCK_NAME_CONFIRMATION.md](MOCK_NAME_CONFIRMATION.md)** - モック名確認

### テストログ・レポート
- **[reports/](reports/)** - バグ報告、新要件分析（Q1～Q6）
- **api_test_*.log** - APIテスト実行ログ（各バージョン）
- **[api_test_q1_q6.sh](api_test_q1_q6.sh)** - テスト実行スクリプト
- **[test_cases_q1_q6.json](test_cases_q1_q6.json)** - テストケース定義
- **[test_q1_q2_conversation.py](test_q1_q2_conversation.py)** - 会話テストスクリプト

---

## 🔙 トップレベルに残した主要ドキュメント

開発・運用で頻繁に参照するドキュメントはトップレベルに残しています：

- **[../README.md](../README.md)** - プロジェクトトップページ
- **[../CLAUDE.md](../CLAUDE.md)** - プロジェクト詳細、API一覧、起動方法
- **[../SYSTEM_OVERVIEW.md](../SYSTEM_OVERVIEW.md)** - システム全体図（最重要）
- **[../INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md)** - セットアップ手順
- **[../DEMO_SCRIPT_FINAL.md](../DEMO_SCRIPT_FINAL.md)** - デモ実施手順
- **[../IMPLEMENTATION_LOG.md](../IMPLEMENTATION_LOG.md)** - 最新の実装作業ログ
- **[../api_test_results.json](../api_test_results.json)** - 最新のテスト結果

---

## 📖 参照方法

必要に応じてこのフォルダ内のドキュメントを参照してください。

**例**: AWSデプロイ方法を知りたい場合
```bash
cat documents/AWS_DEPLOY_GUIDE.md
```

**例**: 過去のバグレポートを確認したい場合
```bash
cat documents/reports/bug_reports/BUG_REPORT.md
```

---

**最終整理日**: 2025-10-24
