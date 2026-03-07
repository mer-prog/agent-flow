# AgentFlow — マルチエージェント AI カスタマーサポートプラットフォーム

LangGraph によるマルチエージェントオーケストレーション、FastMCP ツール連携、RAG ベースのナレッジ検索を統合した、フルスタック AI カスタマーサポートシステム。API キー不要のデモモードと、Claude Haiku 4.5 + OpenAI Embeddings を活用するライブモードの二重動作をサポート。

## Skills Demonstrated

- **Full-Stack Development** — React 19 SPA + FastAPI 非同期バックエンドによるエンドツーエンド開発
- **AI/LLM Integration** — LangGraph マルチエージェントグラフ、Claude Haiku 4.5、RAG パイプライン、FastMCP ツール連携
- **API Design & Integration** — RESTful API 設計（7 ルーター）、SSE ストリーミング、Model Context Protocol 統合
- **Database Design & Management** — PostgreSQL 17 + pgvector によるベクトル検索、非同期 ORM、マイグレーション管理
- **Authentication & Authorization** — JWT 認証（アクセス/リフレッシュトークン）、ロールベースアクセス制御（RBAC）
- **System Architecture** — 5 エージェント + フォーマッターによる状態機械ベースのオーケストレーション
- **UI/UX Design** — Tailwind CSS 4 ダークテーマ、i18n 多言語対応（日英）、リアルタイムストリーミング UI
- **Testing & Quality Assurance** — 54 テストケースによるエージェントロジック・認証・スキーマ検証

## Tech Stack

### バックエンド

| カテゴリ | 技術 |
|---------|------|
| フレームワーク | FastAPI 0.115+ |
| エージェント | LangGraph 0.2+、LangChain Core 0.3+ |
| LLM | Claude Haiku 4.5（langchain-anthropic 0.3+） |
| MCP | FastMCP 2.0+ |
| データベース | PostgreSQL 17 + pgvector 0.3+ |
| ORM | SQLAlchemy 2.0（非同期） + asyncpg 0.30+ |
| マイグレーション | Alembic 1.14+ |
| 埋め込み | OpenAI text-embedding-3-small / SHA-256（デモ） |
| 認証 | python-jose（JWT）+ bcrypt 4.2+ |
| ログ | structlog 24.4+ |
| HTTP クライアント | httpx 0.28+ |

### フロントエンド

| カテゴリ | 技術 |
|---------|------|
| フレームワーク | React 19.0.0 |
| ルーティング | React Router 7.1+ |
| スタイリング | Tailwind CSS 4.0 |
| ビルドツール | Vite 6.0 |
| 言語 | TypeScript 5.7+ |
| 国際化 | i18next 24.2+（日英対応） |
| グラフ描画 | Recharts 2.15+ |
| アイコン | Lucide React 0.468+ |

### インフラ

| カテゴリ | 技術 |
|---------|------|
| コンテナ | Docker マルチステージビルド |
| データベース | pgvector/pgvector:pg17 |
| デプロイ | Render（無料プラン対応） |
| Python ランタイム | 3.12+ |
| パッケージ管理 | uv |

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    React 19 フロントエンド                           │
│           Vite + TypeScript + Tailwind CSS 4 + i18next             │
│                                                                     │
│  Chat │ Tickets │ Escalations │ Knowledge │ Dashboard │ AgentFlow  │
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

## Key Features

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

## Project Structure

```text
agent-flow/
├── app/                          # FastAPI バックエンド
│   ├── main.py                  # エントリーポイント、ミドルウェア設定
│   ├── config.py                # 環境設定（DB、JWT、LLM キー）
│   ├── database.py              # SQLAlchemy 非同期エンジン＆セッション
│   ├── models/                  # SQLAlchemy ORM モデル（8 テーブル）
│   │   ├── user.py             # User、UserRole 列挙型
│   │   ├── conversation.py     # Conversation、ConversationStatus
│   │   ├── message.py          # Message、MessageRole
│   │   ├── ticket.py           # Ticket、TicketStatus、TicketPriority
│   │   ├── escalation.py       # Escalation、EscalationStatus
│   │   ├── agent_run.py        # AgentRun、AgentType
│   │   └── knowledge.py        # KBArticle、KBChunk（pgvector）
│   ├── schemas/                 # Pydantic リクエスト/レスポンススキーマ
│   │   ├── auth.py             # 認証スキーマ
│   │   ├── chat.py             # チャットスキーマ
│   │   ├── conversation.py     # 会話スキーマ
│   │   ├── ticket.py           # チケットスキーマ
│   │   ├── escalation.py       # エスカレーションスキーマ
│   │   ├── knowledge.py        # ナレッジベーススキーマ
│   │   └── stats.py            # 統計スキーマ
│   ├── api/                     # REST API ルーター
│   │   ├── auth.py             # /api/auth
│   │   ├── chat.py             # /api/chat（SSE ストリーミング）
│   │   ├── conversations.py    # /api/conversations
│   │   ├── tickets.py          # /api/tickets
│   │   ├── escalations.py      # /api/escalations
│   │   ├── knowledge.py        # /api/knowledge
│   │   ├── stats.py            # /api/stats
│   │   └── deps.py             # 依存性注入（認証、DB）
│   ├── agents/                  # LangGraph エージェントシステム
│   │   ├── state.py            # AgentState 型定義
│   │   ├── graph.py            # エージェントグラフの構築＆コンパイル
│   │   ├── llm.py              # LLM クライアントシングルトン
│   │   ├── router.py           # ルーターエージェント（意図分類）
│   │   ├── faq.py              # FAQ エージェント（RAG 検索）
│   │   ├── ticket.py           # チケットエージェント（フィールド抽出）
│   │   ├── escalation.py       # エスカレーションエージェント（感情分析）
│   │   ├── chitchat.py         # 雑談エージェント
│   │   └── formatter.py        # レスポンスフォーマッター
│   ├── mcp/                     # FastMCP ツールサーバー
│   │   └── server.py           # 5 つの MCP ツール定義
│   ├── services/                # ビジネスロジック
│   │   ├── auth.py             # 認証ヘルパー
│   │   ├── embedding.py        # 埋め込みサービス（ライブ/デモ切替）
│   │   └── knowledge.py        # ナレッジベース検索＆チャンキング
│   └── core/                    # コアユーティリティ
│       ├── security.py         # JWT/bcrypt
│       └── logging.py          # structlog 設定
├── frontend/                     # React 19 SPA
│   ├── src/
│   │   ├── App.tsx             # ルーティング＆認証ラッパー
│   │   ├── api/client.ts       # HTTP クライアント（自動トークンリフレッシュ）
│   │   ├── hooks/              # カスタムフック（useAuth、useSSE）
│   │   ├── i18n/               # 国際化（en.ts、ja.ts）
│   │   ├── pages/              # ページコンポーネント（8 ページ）
│   │   ├── components/         # 共通コンポーネント
│   │   └── types/              # TypeScript 型定義
│   └── package.json
├── alembic/                      # データベースマイグレーション
│   └── versions/
│       └── 001_initial.py      # 全 8 テーブル + pgvector 拡張の作成
├── tests/                        # テストスイート（54 テスト）
│   ├── test_agents.py          # エージェントロジック
│   ├── test_config.py          # 設定バリデーション
│   ├── test_embedding.py       # 埋め込み生成
│   ├── test_schemas.py         # スキーマ検証
│   └── test_security.py        # JWT/bcrypt
├── docker-compose.yml            # PostgreSQL 17 + pgvector
├── Dockerfile                    # マルチステージビルド
├── render.yaml                   # Render デプロイ設定
├── start.sh                      # 起動スクリプト
└── pyproject.toml                # Python 依存関係＆設定
```

## API Endpoints

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

### ヘルスチェック

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/health` | ヘルスチェック（動作モード表示） |

## Database Schema

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

## AI/ML Pipeline

### エージェントグラフの処理フロー

```text
ユーザーメッセージ
       │
       ▼
  router_agent
  (意図分類: FAQ / Ticket / Escalation / Chitchat)
       │
       ├─── intent: faq ──────→ faq_agent
       │                        ├─ KB ベクトル検索（pgvector）
       │                        └─ 検索結果を基に回答生成
       │
       ├─── intent: ticket ───→ ticket_agent
       │                        ├─ タイトル・優先度・カテゴリ抽出
       │                        └─ チケット自動作成
       │
       ├─── intent: escalation → escalation_agent
       │                         ├─ 感情スコア算出（0.0〜1.0）
       │                         └─ 人間レビューフラグ設定
       │
       └─── intent: chitchat ──→ chitchat_agent
                                 └─ 一般的な会話応答
       │
       ▼
   formatter
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

FastMCP 2.0 により、エージェントは以下のツールを呼び出し可能:

- **search_knowledge_base_tool** — pgvector コサイン類似度によるナレッジベース検索
- **create_ticket** — サポートチケットの作成
- **update_ticket** — チケットステータス・優先度の更新
- **get_support_metrics** — ダッシュボード統計の集計
- **escalate_to_human** — 人間オペレーターへのエスカレーション作成

## Security

### 認証

- JWT トークン（HS256 アルゴリズム）
- アクセストークン: 30 分有効
- リフレッシュトークン: 7 日間有効
- bcrypt によるパスワードハッシュ化

### 認可

- ロールベースアクセス制御（管理者・エージェント・顧客）
- エンドポイント単位の権限チェック
- 顧客データの分離（自分のリソースのみアクセス可能）

### API セキュリティ

- CORS ミドルウェア（許可オリジン設定可能）
- Pydantic によるリクエストバリデーション
- メール形式・パスワード最小長（8 文字）のバリデーション

## Setup

### 前提条件

- Python 3.12+
- Node.js 20+
- Docker（PostgreSQL 用）
- uv（Python パッケージ管理）

### インストール手順

```bash
# 1. PostgreSQL + pgvector を起動
docker compose up -d

# 2. 環境変数を設定
cp .env.example .env
# .env を編集（JWT_SECRET は必ず変更）

# 3. Python 依存関係をインストール
uv sync

# 4. データベースマイグレーションを実行
alembic upgrade head

# 5. バックエンドを起動
uv run fastapi dev app/main.py

# 6. フロントエンドを起動（別ターミナル）
cd frontend && npm install && npm run dev
```

### 環境変数

| 変数名 | 必須 | 説明 | デフォルト |
|--------|------|------|-----------|
| `DATABASE_URL` | はい | PostgreSQL 接続文字列 | — |
| `JWT_SECRET` | はい | JWT 署名用シークレットキー | — |
| `ANTHROPIC_API_KEY` | いいえ | Anthropic API キー（ライブモード用） | — |
| `OPENAI_API_KEY` | いいえ | OpenAI API キー（ライブモード用） | — |
| `APP_ENV` | いいえ | 実行環境 | `development` |
| `LOG_LEVEL` | いいえ | ログレベル | `INFO` |
| `CORS_ORIGINS` | いいえ | CORS 許可オリジン（JSON 配列） | `["http://localhost:5173"]` |

### Docker ビルド（本番環境）

```bash
docker build -t agent-flow .
docker run -p 8000:8000 --env-file .env agent-flow
```

## Testing

```bash
# 全テストを実行
uv run pytest

# 最初の失敗で停止
uv run pytest -x

# 詳細出力
uv run pytest -v
```

### テストカバレッジ

| テストファイル | テスト数 | 対象 |
|--------------|---------|------|
| test_agents.py | 24 | エージェントの意図分類・感情分析・チケット抽出 |
| test_schemas.py | 14 | Pydantic スキーマのバリデーション |
| test_security.py | 8 | JWT トークン生成・検証、パスワードハッシュ |
| test_config.py | 4 | 設定値の読み込み・デフォルト値 |
| test_embedding.py | 4 | 埋め込みの生成・次元数 |

## Design Decisions

### LangGraph によるマルチエージェントオーケストレーション

意図分類 → 専門エージェント → フォーマッターという 3 段階のパイプラインを状態機械として実装。各エージェントが独立して動作し、共有状態（AgentState TypedDict）を通じて連携することで、新しいエージェントの追加や既存エージェントの変更が容易になる設計。

### デュアルモード（ライブ/デモ）

API キーの有無で自動的にモードを切り替えることで、開発者は API コストなしで全機能を試用でき、本番環境ではシームレスに高精度モードに移行可能。デモモードでもアプリケーション全体のフローを完全に動作させることを重視。

### FastMCP によるツール連携

エージェントが利用するツール（ナレッジ検索、チケット操作等）を MCP プロトコルで標準化。ツールの追加・変更がエージェントコードに影響しないデカップリングを実現。

### pgvector によるベクトル検索

専用のベクトルデータベースを導入せず、PostgreSQL の pgvector 拡張を活用。インフラの複雑さを最小限に抑えつつ、コサイン類似度によるセマンティック検索を実現。

### SSE ストリーミング

WebSocket ではなく Server-Sent Events を採用。単方向のストリーミング（サーバー → クライアント）で十分な要件に対して、実装の単純さと HTTP/2 互換性を優先。

### 非同期ファースト

全てのデータベース操作・API ハンドラ・エージェントノードを async/await で実装。I/O バウンドな LLM API 呼び出しやデータベースクエリの並行処理を効率化。

## Running Costs

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

## Author

**@mer-prog**

GitHub: [https://github.com/mer-prog](https://github.com/mer-prog)
