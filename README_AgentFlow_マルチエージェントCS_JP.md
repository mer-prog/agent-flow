# AgentFlow — マルチエージェント AI カスタマーサポートプラットフォーム

> **何を:** LangGraph によるマルチエージェントオーケストレーション、FastMCP ツール連携、RAG ベースのナレッジ検索を統合したフルスタック AI カスタマーサポートシステム
> **誰に:** AI 活用カスタマーサポートの導入を検討する企業・開発チーム
> **技術:** React 19 · FastAPI · LangGraph · FastMCP · PostgreSQL 17 + pgvector · Claude Haiku 4.5

## このプロジェクトで証明できるスキル

| スキル | 実装内容 |
|--------|----------|
| Full-Stack Development | React 19 SPA（TypeScript）+ FastAPI 非同期バックエンドによるエンドツーエンド開発（フロントエンド約 1,500 行、バックエンド約 2,600 行） |
| AI/LLM Integration | LangGraph マルチエージェントグラフ（5 エージェント + フォーマッター）、Claude Haiku 4.5、RAG パイプライン、FastMCP ツール連携、デュアルモード動作 |
| API Design & Integration | RESTful API 設計（7 ルーター、22 エンドポイント）、SSE ストリーミング、MCP Streamable HTTP トランスポート |
| Database Design & Management | PostgreSQL 17 + pgvector による 8 テーブル設計、非同期 ORM（SQLAlchemy 2.0 + asyncpg）、Alembic マイグレーション |
| Authentication & Authorization | JWT 認証（アクセス/リフレッシュトークン）、ロールベースアクセス制御（管理者・エージェント・顧客の 3 ロール） |
| System Architecture | 状態機械ベースのマルチエージェントオーケストレーション、MCP によるツールデカップリング、Docker マルチステージビルド |
| UI/UX Design | Tailwind CSS 4 ダークテーマ、i18next による日英多言語対応、SSE リアルタイムストリーミング UI、Recharts グラフ可視化 |

## 技術スタック

### バックエンド

| カテゴリ | 技術 | 用途 |
|----------|------|------|
| フレームワーク | FastAPI >=0.115 | 非同期 REST API サーバー |
| エージェント | LangGraph >=0.2、LangChain Core >=0.3 | マルチエージェントグラフのオーケストレーション |
| LLM | langchain-anthropic >=0.3（Claude Haiku 4.5） | 意図分類・応答生成・感情分析 |
| 埋め込み | langchain-openai >=0.3（text-embedding-3-small） | ナレッジベースのベクトル埋め込み |
| MCP | FastMCP >=2.0 | エージェントツールの標準化プロトコル |
| データベース | PostgreSQL 17 + pgvector >=0.3 | リレーショナルデータ + ベクトル検索 |
| ORM | SQLAlchemy >=2.0（非同期）+ asyncpg >=0.30 | 非同期データベースアクセス |
| マイグレーション | Alembic >=1.14 | データベーススキーマ管理 |
| 認証 | python-jose >=3.3 + bcrypt >=4.2 | JWT トークン生成・パスワードハッシュ |
| 設定管理 | pydantic-settings >=2.7 | 環境変数の型安全な読み込み |
| ログ | structlog >=24.4 | 構造化ログ出力 |
| HTTP クライアント | httpx >=0.28 | 外部 API 通信 |

### フロントエンド

| カテゴリ | 技術 | 用途 |
|----------|------|------|
| フレームワーク | React ^19.0.0 | UI コンポーネント |
| ルーティング | React Router ^7.1.0 | SPA ルーティング |
| スタイリング | Tailwind CSS ^4.0.0 | ユーティリティファースト CSS |
| ビルドツール | Vite ^6.0.0 | 高速ビルド・HMR |
| 言語 | TypeScript ^5.7.0 | 型安全な開発 |
| 国際化 | i18next ^24.2.0 + react-i18next ^15.4.0 | 日英多言語対応 |
| グラフ | Recharts ^2.15.0 | ダッシュボード統計の可視化 |
| アイコン | Lucide React ^0.468.0 | UI アイコン |

### インフラ

| カテゴリ | 技術 | 用途 |
|----------|------|------|
| コンテナ | Docker マルチステージビルド | フロントエンドビルド + バックエンド実行 |
| データベースイメージ | pgvector/pgvector:pg17 | ベクトル拡張付き PostgreSQL |
| デプロイ | Render（無料プラン対応） | Web サービス + マネージド PostgreSQL |
| Python ランタイム | 3.12+ | バックエンド実行環境 |
| パッケージ管理 | uv | Python 依存関係管理 |

## アーキテクチャ概要

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    React 19 フロントエンド                           │
│           Vite + TypeScript + Tailwind CSS 4 + i18next             │
│                                                                     │
│  Chat │ Tickets │ Escalations │ Knowledge │ Dashboard │ AgentFlow  │
│  Settings │ Login                                                   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP / SSE
                            ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        FastAPI バックエンド                            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  API ルーター（7 本）                                            │  │
│  │  auth │ chat │ conversations │ tickets │ escalations │          │  │
│  │  knowledge │ stats                                              │  │
│  └───────────────────────────┬─────────────────────────────────────┘  │
│                              │                                        │
│  ┌───────────────────────────▼─────────────────────────────────────┐  │
│  │           LangGraph マルチエージェントグラフ                      │  │
│  │                                                                 │  │
│  │  router_agent ──┬──→ faq_agent ────────┐                       │  │
│  │  (意図分類)      ├──→ ticket_agent ─────┤                       │  │
│  │                  ├──→ escalation_agent ──┤──→ formatter → END   │  │
│  │                  └──→ chitchat_agent ────┘   (応答整形)          │  │
│  │                                                                 │  │
│  │  ライブモード: Claude Haiku 4.5 + OpenAI Embeddings            │  │
│  │  デモモード: キーワード分類 + SHA-256 擬似埋め込み               │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  FastMCP ツールサーバー（5 ツール）                               │  │
│  │  search_knowledge_base │ create_ticket │ update_ticket │        │  │
│  │  get_support_metrics │ escalate_to_human                        │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  サービス層                                                      │  │
│  │  auth │ embedding │ knowledge │ security                        │  │
│  └───────────────────────────┬─────────────────────────────────────┘  │
└──────────────────────────────┼────────────────────────────────────────┘
                               │
              ┌────────────────┴─────────────────┐
              ▼                                  ▼
  ┌─────────────────────┐           ┌──────────────────────┐
  │  PostgreSQL 17      │           │  外部 API            │
  │  + pgvector         │           │  Anthropic (Claude)  │
  │                     │           │  OpenAI (Embeddings) │
  │  8 テーブル:         │           └──────────────────────┘
  │  users              │
  │  conversations      │
  │  messages           │
  │  tickets            │
  │  escalations        │
  │  agent_runs         │
  │  kb_articles        │
  │  kb_chunks          │
  └─────────────────────┘
```

## 主要機能

### マルチエージェントチャットシステム

- **意図分類ルーター** — ユーザーメッセージを FAQ・チケット・エスカレーション・雑談の 4 カテゴリに自動分類
- **RAG ベース FAQ 応答** — pgvector によるベクトル類似度検索でナレッジベースから関連情報を取得し、回答を生成
- **自動チケット作成** — 会話内容からタイトル・優先度・カテゴリを抽出し、サポートチケットを自動生成
- **感情分析エスカレーション** — ネガティブな感情を検知し、人間のオペレーターへのエスカレーションを提案
- **SSE リアルタイムストリーミング** — トークン単位でのリアルタイム応答表示

### デュアルモード動作

- **ライブモード** — Claude Haiku 4.5 による高精度な自然言語処理 + OpenAI text-embedding-3-small による意味検索
- **デモモード** — API キー不要。キーワードベースの分類器 + SHA-256 擬似埋め込みで全機能を体験可能

### ナレッジベース管理

- 記事の作成・編集・削除（CRUD）
- 自動チャンキング＆埋め込み生成
- コサイン類似度によるベクトル検索
- カテゴリフィルタリング・公開状態管理

### チケット管理

- 優先度 4 段階（低・中・高・緊急）
- ステータス追跡（オープン・対応中・解決済み・クローズ）
- ロールベースの表示制御（顧客は自分のチケットのみ、エージェント/管理者は全件）

### エスカレーション管理

- 保留中エスカレーションの一覧表示
- 感情スコアによる優先度判断
- 承認・却下ワークフロー

### ダッシュボード＆分析

- 会話・チケット・エスカレーション統計
- エージェントパフォーマンスメトリクス
- 解決率・応答時間の可視化（Recharts）

### 認証＆認可

- JWT トークン（アクセス + リフレッシュ）
- 3 つのユーザーロール: 管理者・エージェント・顧客
- 401 時の自動トークンリフレッシュ

### 多言語対応

- i18next による日本語・英語の切り替え
- ブラウザ言語自動検出

## プロジェクト構成

```text
agent-flow/
├── app/                          # FastAPI バックエンド（約 2,600 行）
│   ├── main.py                  # エントリーポイント、ミドルウェア設定（67 行）
│   ├── config.py                # 環境設定、デュアルモード判定（82 行）
│   ├── database.py              # SQLAlchemy 非同期エンジン＆セッション（30 行）
│   ├── models/                  # SQLAlchemy ORM モデル（8 テーブル）
│   │   ├── user.py             # User、UserRole 列挙型（41 行）
│   │   ├── conversation.py     # Conversation、ConversationStatus（41 行）
│   │   ├── message.py          # Message、MessageRole（34 行）
│   │   ├── ticket.py           # Ticket、TicketStatus、TicketPriority（65 行）
│   │   ├── escalation.py       # Escalation、EscalationStatus（51 行）
│   │   ├── agent_run.py        # AgentRun、AgentType、AgentRunStatus（50 行）
│   │   └── knowledge.py        # KBArticle、KBChunk + pgvector（46 行）
│   ├── schemas/                 # Pydantic リクエスト/レスポンススキーマ
│   │   ├── auth.py             # 認証スキーマ（38 行）
│   │   ├── chat.py             # チャットスキーマ（15 行）
│   │   ├── conversation.py     # 会話スキーマ（44 行）
│   │   ├── ticket.py           # チケットスキーマ（44 行）
│   │   ├── escalation.py       # エスカレーションスキーマ（32 行）
│   │   ├── knowledge.py        # ナレッジベーススキーマ（60 行）
│   │   └── stats.py            # 統計スキーマ（23 行）
│   ├── api/                     # REST API ルーター（7 本）
│   │   ├── auth.py             # /api/auth — 登録・ログイン・リフレッシュ（59 行）
│   │   ├── chat.py             # /api/chat — SSE ストリーミング（136 行）
│   │   ├── conversations.py    # /api/conversations — 会話 CRUD（105 行）
│   │   ├── tickets.py          # /api/tickets — チケット管理（103 行）
│   │   ├── escalations.py      # /api/escalations — エスカレーション管理（90 行）
│   │   ├── knowledge.py        # /api/knowledge — ナレッジベース CRUD + 検索（141 行）
│   │   ├── stats.py            # /api/stats — ダッシュボード統計（101 行）
│   │   └── deps.py             # 依存性注入（認証、DB セッション）（49 行）
│   ├── agents/                  # LangGraph エージェントシステム
│   │   ├── state.py            # AgentState TypedDict 定義（19 行）
│   │   ├── graph.py            # エージェントグラフの構築＆コンパイル（67 行）
│   │   ├── llm.py              # LLM クライアントシングルトン（22 行）
│   │   ├── router.py           # ルーターエージェント — 意図分類（109 行）
│   │   ├── faq.py              # FAQ エージェント — RAG 検索＆応答生成（89 行）
│   │   ├── ticket.py           # チケットエージェント — フィールド抽出（114 行）
│   │   ├── escalation.py       # エスカレーションエージェント — 感情分析（99 行）
│   │   ├── chitchat.py         # 雑談エージェント（73 行）
│   │   └── formatter.py        # レスポンスフォーマッター（35 行）
│   ├── mcp/                     # FastMCP ツールサーバー
│   │   └── server.py           # 5 つの MCP ツール定義（196 行）
│   ├── services/                # ビジネスロジック
│   │   ├── auth.py             # 認証ヘルパー（58 行）
│   │   ├── embedding.py        # 埋め込みサービス — ライブ/デモ切替（40 行）
│   │   └── knowledge.py        # ナレッジベース検索＆チャンキング（89 行）
│   └── core/                    # コアユーティリティ
│       ├── security.py         # JWT トークン生成・検証、bcrypt（32 行）
│       └── logging.py          # structlog 設定（26 行）
├── frontend/                     # React 19 SPA（約 1,500 行）
│   ├── src/
│   │   ├── App.tsx             # ルーティング＆認証ラッパー（42 行）
│   │   ├── api/client.ts       # HTTP クライアント — 自動トークンリフレッシュ（70 行）
│   │   ├── hooks/
│   │   │   ├── useAuth.ts     # 認証フック（52 行）
│   │   │   └── useSSE.ts      # SSE ストリーミングフック（75 行）
│   │   ├── i18n/
│   │   │   ├── config.ts      # i18next 初期化（16 行）
│   │   │   ├── en.ts          # 英語翻訳（69 行）
│   │   │   └── ja.ts          # 日本語翻訳（69 行）
│   │   ├── pages/              # ページコンポーネント（8 ページ）
│   │   │   ├── LoginPage.tsx  # ログイン/登録画面（109 行）
│   │   │   ├── ChatPage.tsx   # チャット画面 — SSE 対応（173 行）
│   │   │   ├── TicketsPage.tsx # チケット一覧・作成（100 行）
│   │   │   ├── EscalationsPage.tsx # エスカレーション管理（123 行）
│   │   │   ├── KnowledgePage.tsx   # ナレッジベース管理（175 行）
│   │   │   ├── DashboardPage.tsx   # ダッシュボード — Recharts（131 行）
│   │   │   ├── AgentFlowPage.tsx   # エージェントフロー可視化（116 行）
│   │   │   └── SettingsPage.tsx    # 設定 — 言語切替・モード表示（53 行）
│   │   ├── components/
│   │   │   └── Layout.tsx     # 共通レイアウト — サイドバー＆ナビ（96 行）
│   │   └── types/
│   │       └── index.ts       # TypeScript 型定義（87 行）
│   └── package.json
├── scripts/
│   └── seed.py                  # シードデータ — デモユーザー・KB 記事・チケット（174 行）
├── alembic/                      # データベースマイグレーション
│   └── versions/
│       └── 001_initial.py      # 全 8 テーブル + pgvector 拡張
├── tests/                        # テストスイート（54 テスト）
│   ├── test_agents.py          # エージェントロジック（20 テスト）
│   ├── test_config.py          # 設定バリデーション（8 テスト）
│   ├── test_embedding.py       # 埋め込み生成（6 テスト）
│   ├── test_schemas.py         # スキーマ検証（14 テスト）
│   └── test_security.py       # JWT/bcrypt（6 テスト）
├── docker-compose.yml            # PostgreSQL 17 + pgvector
├── Dockerfile                    # マルチステージビルド（Node.js + Python）
├── render.yaml                   # Render デプロイ設定
├── start.sh                      # 起動スクリプト（マイグレーション + シード + 起動）
└── pyproject.toml                # Python 依存関係＆設定
```

## API エンドポイント

### 認証（/api/auth）

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/api/auth/register` | ユーザー登録 |
| POST | `/api/auth/login` | ログイン（トークン発行） |
| POST | `/api/auth/refresh` | アクセストークンのリフレッシュ |
| GET | `/api/auth/me` | 現在のユーザー情報取得 |

### チャット（/api/chat）

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/api/chat` | メッセージ送信（SSE ストリーミング応答） |
| GET | `/api/chat/{conversation_id}/history` | 会話履歴の取得 |

### 会話管理（/api/conversations）

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/api/conversations` | 会話一覧（ページネーション対応） |
| GET | `/api/conversations/{id}` | 会話詳細（メッセージ含む） |
| PATCH | `/api/conversations/{id}` | 会話の更新（タイトル/ステータス） |
| DELETE | `/api/conversations/{id}` | 会話の削除 |

### チケット（/api/tickets）

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/api/tickets` | チケット一覧（ロール別表示） |
| POST | `/api/tickets` | チケット作成 |
| GET | `/api/tickets/{id}` | チケット詳細 |
| PATCH | `/api/tickets/{id}` | チケット更新 |

### エスカレーション（/api/escalations）

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/api/escalations` | エスカレーション一覧（管理者/エージェントのみ） |
| GET | `/api/escalations/{id}` | エスカレーション詳細 |
| POST | `/api/escalations/{id}/review` | エスカレーションのレビュー（承認/却下） |

### ナレッジベース（/api/knowledge）

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/api/knowledge` | 公開記事一覧 |
| POST | `/api/knowledge` | 記事作成（管理者/エージェント） |
| GET | `/api/knowledge/{id}` | 記事詳細（チャンク含む） |
| PATCH | `/api/knowledge/{id}` | 記事更新（内容変更時は再チャンキング） |
| DELETE | `/api/knowledge/{id}` | 記事削除 |
| POST | `/api/knowledge/search` | ベクトル類似度検索 |

### 統計（/api/stats）

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/api/stats` | ダッシュボード統計 |
| GET | `/api/stats/agent-performance` | エージェントパフォーマンス |

### ヘルスチェック・MCP

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/health` | ヘルスチェック（動作モード表示） |
| — | `/mcp` | FastMCP Streamable HTTP エンドポイント |

## データベース設計

### テーブル定義

| テーブル | 主要カラム | 説明 |
|---------|-----------|------|
| **users** | id (UUID), email, hashed_password, full_name, role, is_active | ユーザーアカウント |
| **conversations** | id (UUID), user_id (FK), title, status, metadata (JSONB) | チャット会話 |
| **messages** | id (UUID), conversation_id (FK), role, content, metadata (JSONB) | 会話内メッセージ |
| **tickets** | id (UUID), conversation_id (FK), user_id (FK), title, description, status, priority, category, assigned_to (FK) | サポートチケット |
| **escalations** | id (UUID), conversation_id (FK), ticket_id (FK), reason, sentiment_score, status, reviewed_by (FK), notes | エスカレーション |
| **agent_runs** | id (UUID), conversation_id (FK), agent_type, input_data (JSONB), output_data (JSONB), duration_ms, status | エージェント実行ログ |
| **kb_articles** | id (UUID), title, content, category, is_published | ナレッジベース記事 |
| **kb_chunks** | id (UUID), article_id (FK), content, embedding (Vector(1536)), chunk_index | 埋め込みチャンク |

### 列挙型

| 列挙型 | 値 |
|--------|-----|
| UserRole | admin, agent, customer |
| ConversationStatus | active, closed, archived |
| MessageRole | user, assistant, system |
| TicketStatus | open, in_progress, resolved, closed |
| TicketPriority | low, medium, high, urgent |
| EscalationStatus | pending, approved, rejected, completed |
| AgentType | router, faq, ticket, escalation, chitchat, formatter |
| AgentRunStatus | started, completed, failed |

## AI アルゴリズム / ロジック詳細

### エージェントグラフの処理フロー

```text
ユーザーメッセージ
       │
       ▼
  router_agent（109 行）
  (意図分類: FAQ / Ticket / Escalation / Chitchat)
       │
       ├─── intent: faq ──────→ faq_agent（89 行）
       │                        ├─ KB ベクトル検索（pgvector コサイン類似度）
       │                        └─ 検索結果を基に回答生成
       │
       ├─── intent: ticket ───→ ticket_agent（114 行）
       │                        ├─ タイトル・優先度・カテゴリ抽出
       │                        └─ チケット自動作成
       │
       ├─── intent: escalation → escalation_agent（99 行）
       │                         ├─ 感情スコア算出（0.0〜1.0）
       │                         └─ 人間レビューフラグ設定
       │
       └─── intent: chitchat ──→ chitchat_agent（73 行）
                                 └─ 一般的な会話応答
       │
       ▼
   formatter（35 行）
   (最終応答の整形・メタデータ付与)
       │
       ▼
   SSE ストリーミングで応答返却
```

### デュアルモード実装

| コンポーネント | ライブモード | デモモード |
|--------------|------------|-----------|
| 意図分類 | Claude Haiku 4.5 | 正規表現パターンマッチング |
| FAQ 応答 | Claude Haiku 4.5 + KB 検索 | テンプレート応答 |
| チケット抽出 | Claude Haiku 4.5 | 正規表現フィールド抽出 |
| 感情分析 | Claude Haiku 4.5（0.0〜1.0） | キーワードベース分析 |
| 雑談応答 | Claude Haiku 4.5 | テンプレート応答 |
| 埋め込み生成 | OpenAI text-embedding-3-small | SHA-256 擬似埋め込み |

### MCP ツール連携

FastMCP 2.0 により、エージェントは以下のツールを呼び出し可能（Streamable HTTP トランスポートで `/mcp` にマウント）:

- **search_knowledge_base_tool** — pgvector コサイン類似度によるナレッジベース検索
- **create_ticket** — サポートチケットの作成
- **update_ticket** — チケットステータス・優先度の更新
- **get_support_metrics** — ダッシュボード統計の集計
- **escalate_to_human** — 人間オペレーターへのエスカレーション作成

## セキュリティ設計

### 認証

- JWT トークン（HS256 アルゴリズム）
- アクセストークン: 30 分有効
- リフレッシュトークン: 7 日間有効
- bcrypt によるパスワードハッシュ化

### 認可

- ロールベースアクセス制御（管理者・エージェント・顧客）
- エンドポイント単位の権限チェック（deps.py の依存性注入）
- 顧客データの分離（自分のリソースのみアクセス可能）

### API セキュリティ

- CORS ミドルウェア（許可オリジン設定可能）
- Pydantic によるリクエストバリデーション
- メール形式・パスワード最小長（8 文字）のバリデーション

## シードデータ

起動スクリプト（`start.sh`）により、初回起動時にデモ用データが自動投入される:

| データ種別 | 内容 |
|-----------|------|
| ユーザー | 管理者（admin@example.com）、エージェント（agent@example.com）、顧客（demo@example.com） |
| ナレッジベース記事 | 5 記事（利用開始ガイド、料金プラン、返品ポリシー、技術要件、アカウントセキュリティ） |
| チケット | 3 件（パスワードリセット、二重請求、機能リクエスト） |
| 会話 | 1 件（料金問い合わせ） |

> シードパスワードは環境変数 `SEED_ADMIN_PASSWORD`、`SEED_AGENT_PASSWORD`、`SEED_CUSTOMER_PASSWORD` で上書き可能。冪等性あり（既存データがある場合はスキップ）。

## テスト構成

```bash
# 全テストを実行
uv run pytest

# 最初の失敗で停止
uv run pytest -x

# 詳細出力
uv run pytest -v
```

| テストファイル | テスト数 | 対象 |
|--------------|---------|------|
| test_agents.py | 20 | エージェントの意図分類・感情分析・チケット抽出・デモモード動作 |
| test_schemas.py | 14 | Pydantic スキーマのバリデーション・シリアライズ |
| test_config.py | 8 | 設定値の読み込み・デフォルト値・デュアルモード判定 |
| test_embedding.py | 6 | 埋め込みの生成・次元数・デモモード SHA-256 |
| test_security.py | 6 | JWT トークン生成・検証、パスワードハッシュ |
| **合計** | **54** | |

## セットアップ

### 前提条件

- Python 3.12+
- Node.js 20+
- Docker（PostgreSQL 用）
- uv（Python パッケージ管理）

### インストール手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/mer-prog/agent-flow.git
cd agent-flow

# 2. PostgreSQL + pgvector を起動
docker compose up -d

# 3. 環境変数を設定
cp .env.example .env
# .env を編集（JWT_SECRET は必ず変更）

# 4. Python 依存関係をインストール
uv sync

# 5. データベースマイグレーションを実行
alembic upgrade head

# 6. バックエンドを起動
uv run fastapi dev app/main.py

# 7. フロントエンドを起動（別ターミナル）
cd frontend && npm install && npm run dev
```

### 環境変数

| 変数名 | 説明 | 必須 | デフォルト |
|--------|------|------|-----------|
| `DATABASE_URL` | PostgreSQL 接続文字列 | はい | — |
| `JWT_SECRET` | JWT 署名用シークレットキー | はい | — |
| `ANTHROPIC_API_KEY` | Anthropic API キー（ライブモード用） | いいえ | — |
| `OPENAI_API_KEY` | OpenAI API キー（ライブモード用） | いいえ | — |
| `APP_ENV` | 実行環境 | いいえ | `development` |
| `LOG_LEVEL` | ログレベル | いいえ | `INFO` |
| `CORS_ORIGINS` | CORS 許可オリジン（JSON 配列） | いいえ | `["http://localhost:5173"]` |

### Docker ビルド（本番環境）

```bash
docker build -t agent-flow .
docker run -p 8000:8000 --env-file .env agent-flow
```

## 設計判断の根拠

| 判断 | 根拠 |
|------|------|
| LangGraph マルチエージェント | 意図分類 → 専門エージェント → フォーマッターの 3 段階パイプラインを状態機械として実装。共有状態（AgentState TypedDict）による疎結合設計でエージェントの追加・変更が容易 |
| デュアルモード（ライブ/デモ） | API キーの有無で自動切替。開発者は API コスト不要で全機能を試用でき、本番環境ではシームレスに高精度モードへ移行可能 |
| FastMCP ツール連携 | エージェントが利用するツールを MCP プロトコルで標準化。ツールの追加・変更がエージェントコードに影響しないデカップリングを実現 |
| pgvector ベクトル検索 | 専用ベクトル DB を導入せず PostgreSQL 拡張を活用。インフラの複雑さを最小限に抑えつつコサイン類似度検索を実現 |
| SSE ストリーミング | WebSocket ではなく Server-Sent Events を採用。単方向ストリーミングで十分な要件に対して実装の単純さと HTTP/2 互換性を優先 |
| 非同期ファースト | 全 DB 操作・API ハンドラ・エージェントノードを async/await で実装。I/O バウンドな LLM API 呼び出しと DB クエリの並行処理を効率化 |
| Docker マルチステージビルド | フロントエンドビルド（Node.js）とバックエンド実行（Python）を分離し、本番イメージサイズを最小化 |

## 運用コスト

### 無料枠での運用

| サービス | プラン | 月額コスト |
|---------|-------|-----------|
| Render Web Service | Free | $0 |
| Render PostgreSQL | Free | $0 |
| **合計（デモモード）** | | **$0** |

### ライブモード（API キー使用時）の追加コスト

| サービス | 料金体系 | 目安コスト |
|---------|---------|-----------|
| Anthropic Claude Haiku 4.5 | 入力 $0.80/100万トークン、出力 $4.00/100万トークン | 月 $1〜5（軽量利用時） |
| OpenAI Embeddings (text-embedding-3-small) | $0.02/100万トークン | 月 $0.01〜0.10 |
| **合計（ライブモード）** | | **月 $1〜5 程度** |

> デモモードでは API キー不要のため、完全無料で動作します。

## 作者

**[@mer-prog](https://github.com/mer-prog)**
