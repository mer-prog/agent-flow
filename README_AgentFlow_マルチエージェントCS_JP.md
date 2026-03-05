# AgentFlow — マルチエージェント カスタマーサポート基盤

> **何を:** LangGraph による5つの専門AIエージェントを協調動作させ、FAQ応答・チケット管理・エスカレーション・雑談を自動処理するカスタマーサポートプラットフォーム
>
> **誰に:** AIエージェント・オーケストレーション、RAG、Human-in-the-Loop の実装パターンを求めるエンジニア
>
> **技術:** LangGraph · FastMCP · FastAPI · React 19 · PostgreSQL 17 · pgvector · Tailwind CSS 4

ソースコード: [https://github.com/mer-prog/agent-flow](https://github.com/mer-prog/agent-flow)

---

## このプロジェクトで証明できるスキル

| スキル | 実装内容 |
|--------|----------|
| マルチエージェント設計 | LangGraph StateGraph で Router → 4専門エージェント → Formatter の条件分岐グラフを構築。TypedDict による型安全な状態管理 |
| RAG パイプライン | pgvector によるコサイン類似度検索、文単位チャンキング（~500文字）、1536次元ベクトル埋め込みによるナレッジベース検索 |
| デュアルモード設計 | APIキー不要のデモモード（キーワード分類 + SHA-256疑似埋め込み）とLLMフル活用のライブモードを自動切り替え |
| リアルタイムストリーミング | Server-Sent Events によるエージェントトレース + トークン単位のチャット応答ストリーミング |
| 非同期アーキテクチャ | FastAPI + SQLAlchemy 2.0 async + asyncpg による完全非同期のDB操作・APIハンドラ・エージェントノード |
| MCP サーバー実装 | FastMCP で5つのツールを Streamable HTTP トランスポートで公開。外部AIクライアントからのツール呼び出しに対応 |
| 認証・認可 | JWT HS256（アクセス/リフレッシュトークン）+ bcrypt パスワードハッシュ + ロールベースアクセス制御（admin/agent/customer） |

---

## 技術スタック

| カテゴリ | 技術 | 用途 |
|----------|------|------|
| バックエンド | Python >=3.12, FastAPI >=0.115 | 非同期 REST API サーバー |
| エージェント基盤 | LangGraph >=0.2 | StateGraph によるマルチエージェントオーケストレーション |
| LLM | langchain-anthropic >=0.3 (Claude Haiku 4.5) | インテント分類・応答生成・感情分析 |
| 埋め込み | langchain-openai >=0.3 (text-embedding-3-small) | 1536次元ベクトル埋め込み生成 |
| MCP | FastMCP >=2.0 | Model Context Protocol サーバー（5ツール） |
| データベース | PostgreSQL 17 + pgvector >=0.3 | リレーショナルDB + ベクトル類似度検索 |
| ORM | SQLAlchemy[asyncio] >=2.0, asyncpg >=0.30 | 非同期データベース操作 |
| マイグレーション | Alembic >=1.14 | 非同期DBスキーママイグレーション |
| 認証 | python-jose[cryptography] >=3.3, bcrypt >=4.2 | JWT トークン発行・パスワードハッシュ |
| ログ | structlog >=24.4 | 構造化ログ（開発: コンソール / 本番: JSON） |
| 設定管理 | pydantic-settings >=2.7 | 型安全な環境変数管理 |
| フロントエンド | React ^19.0.0, React DOM ^19.0.0 | SPA UI |
| ルーティング | React Router DOM ^7.1.0 | クライアントサイドルーティング |
| 国際化 | i18next ^24.2.0, react-i18next ^15.4.0 | 日本語・英語の多言語対応 |
| グラフ描画 | recharts ^2.15.0 | ダッシュボードのKPIチャート |
| アイコン | lucide-react ^0.468.0 | UIアイコン |
| スタイリング | Tailwind CSS ^4.0.0 | ユーティリティファーストCSS（ダークテーマ） |
| ビルド | Vite ^6.0.0, TypeScript ^5.7.0 | 高速ビルド + 厳密型チェック |
| テスト | pytest >=8.0, pytest-asyncio >=0.24 | 非同期対応テストフレームワーク |
| コンテナ | Docker Compose (pgvector/pgvector:pg17) | ローカル開発用PostgreSQL |

---

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────────┐
│                     フロントエンド (React 19)                    │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │ログイン│ │ダッシュ│ │チャット│ │チケット│ │エスカレ│ │ナレッジ│       │
│  │      │ │ボード │ │(SSE) │ │      │ │ーション│ │ベース │       │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘       │
│     └────────┴────────┴────────┴────────┴────────┘            │
│                         │ HTTP / SSE                           │
└─────────────────────────┼─────────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────────┐
│                   FastAPI バックエンド                          │
│  ┌──────────────────────┼──────────────────────────────────┐  │
│  │              REST API ルーター (7モジュール)               │  │
│  │  auth · chat · conversations · tickets                   │  │
│  │  escalations · knowledge · stats                         │  │
│  └──────────────────────┼──────────────────────────────────┘  │
│                         │                                      │
│  ┌──────────────────────┼──────────────────────────────────┐  │
│  │            LangGraph エージェントグラフ                    │  │
│  │                                                          │  │
│  │              ┌──────────┐                                │  │
│  │   START ───▶ │  Router  │                                │  │
│  │              └────┬─────┘                                │  │
│  │       ┌───────┬───┴───┬───────┐                         │  │
│  │       ▼       ▼       ▼       ▼                         │  │
│  │    ┌─────┐ ┌──────┐ ┌─────┐ ┌──────┐                   │  │
│  │    │ FAQ │ │Ticket│ │Esca.│ │Chat  │                    │  │
│  │    │(RAG)│ │      │ │(HITL)│ │      │                    │  │
│  │    └──┬──┘ └──┬───┘ └──┬──┘ └──┬───┘                   │  │
│  │       └───────┴────────┴───────┘                        │  │
│  │                    │                                     │  │
│  │           ┌────────▼────────┐                           │  │
│  │           │   Formatter     │                            │  │
│  │           └────────┬────────┘                           │  │
│  │                   END                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                      │
│  ┌──────────────┐  ┌────┴───────┐  ┌───────────────────────┐  │
│  │ FastMCP (5T) │  │サービス層   │  │ セキュリティ           │  │
│  │ /mcp         │  │auth/embed/ │  │ JWT + bcrypt + RBAC   │  │
│  │              │  │knowledge   │  │                       │  │
│  └──────────────┘  └────┬───────┘  └───────────────────────┘  │
└─────────────────────────┼─────────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────────┐
│              PostgreSQL 17 + pgvector                          │
│  ┌──────┐ ┌──────────┐ ┌────────┐ ┌──────┐ ┌──────────────┐  │
│  │users │ │conversa- │ │messages│ │ticket│ │kb_articles   │  │
│  │      │ │tions     │ │        │ │      │ │+ kb_chunks   │  │
│  │      │ │          │ │        │ │      │ │(VECTOR 1536) │  │
│  └──────┘ └──────────┘ └────────┘ └──────┘ └──────────────┘  │
│  ┌───────────┐ ┌─────────────┐                                │
│  │escalations│ │ agent_runs  │                                │
│  └───────────┘ └─────────────┘                                │
└───────────────────────────────────────────────────────────────┘
```

---

## 主要機能

### 1. マルチエージェントオーケストレーション
LangGraph の StateGraph を使用し、6ノード構成のエージェントグラフを実装。Router エージェントがユーザーの意図を分類（faq / ticket / escalation / chitchat）し、対応する専門エージェントへ条件分岐でルーティング。全エージェントの実行結果は Formatter ノードで統合。`agent_trace` リストで各ノードの実行時間・メタデータを追跡する監査証跡を提供。

### 2. RAG ナレッジベース検索
ナレッジベース記事を文単位で約500文字のチャンクに分割し、各チャンクに1536次元のベクトル埋め込みを生成。ユーザーのクエリをベクトル化し、pgvector のコサイン類似度検索で関連チャンクを取得。FAQ エージェントがこのコンテキストを使用してLLMに回答を生成させる。

### 3. デュアルモード動作
- **デモモード**（APIキー未設定）: キーワード正規表現による意図分類、SHA-256ベースの決定論的疑似埋め込み（1536次元）、テンプレート応答。外部API費用ゼロで全機能動作。
- **ライブモード**（`ANTHROPIC_API_KEY` + `OPENAI_API_KEY` 設定済み）: Claude Haiku 4.5 によるインテント分類・応答生成・感情分析、OpenAI text-embedding-3-small による実ベクトル埋め込み。

### 4. リアルタイムチャットストリーミング
POST `/api/chat` エンドポイントが Server-Sent Events でエージェントトレースとトークンをリアルタイム配信。フロントエンドの `useSSE` カスタムフックが ReadableStream を逐次パースし、ストリーミングテキストを表示。

### 5. Human-in-the-Loop エスカレーション
エスカレーションエージェントがユーザーメッセージの感情スコア（0.0〜1.0）を算出し、`require_human_review = true` フラグを設定。管理者・エージェントが承認/却下アクションで対応。

### 6. MCP ツールサーバー
FastMCP で5つのツールを Streamable HTTP トランスポートで `/mcp` に公開。外部AIクライアント（Claude Desktop等）からナレッジ検索、チケット作成・更新、メトリクス取得、エスカレーション作成が可能。

### 7. JWT 認証 + ロールベースアクセス制御
bcrypt によるパスワードハッシュ、HS256 JWT（アクセストークン30分 / リフレッシュトークン7日）。3ロール（admin / agent / customer）によるエンドポイントレベルのアクセス制御。顧客は自身のリソースのみ参照可能、エージェント・管理者は全データにアクセス可能。

### 8. ダッシュボード分析
会話数・アクティブ会話・オープンチケット・保留エスカレーション・解決率・平均応答時間のKPIカードと、エージェント別実行回数の棒グラフ・円グラフを recharts で描画。

### 9. 多言語対応（i18n）
i18next + react-i18next による日本語・英語切り替え。ブラウザ言語自動検出、設定画面からの手動切り替え対応。

---

## プロジェクト構成

```
agent-flow/
├── app/                              # バックエンド (Python)
│   ├── main.py                       # FastAPI アプリ起動・ルーター登録 (68行)
│   ├── config.py                     # pydantic-settings 設定管理 (82行)
│   ├── database.py                   # SQLAlchemy 非同期エンジン (31行)
│   ├── agents/                       # LangGraph エージェント群
│   │   ├── state.py                  #   AgentState TypedDict (20行)
│   │   ├── graph.py                  #   StateGraph 構築・コンパイル (68行)
│   │   ├── llm.py                    #   ChatAnthropic シングルトン (23行)
│   │   ├── router.py                 #   意図分類エージェント (110行)
│   │   ├── faq.py                    #   RAG FAQ エージェント (90行)
│   │   ├── ticket.py                 #   チケット作成エージェント (115行)
│   │   ├── escalation.py             #   感情分析・エスカレーション (100行)
│   │   ├── chitchat.py               #   雑談エージェント (74行)
│   │   ├── formatter.py              #   レスポンス整形 (36行)
│   │   └── __init__.py               #   共通ユーティリティ (13行)
│   ├── mcp/
│   │   └── server.py                 # FastMCP サーバー + 5ツール (197行)
│   ├── services/
│   │   ├── auth.py                   # ユーザー登録・認証・トークン (59行)
│   │   ├── embedding.py              # デュアルモード埋め込み (41行)
│   │   └── knowledge.py              # KB検索・チャンキング (90行)
│   ├── core/
│   │   ├── security.py               # bcrypt + JWT ユーティリティ (33行)
│   │   └── logging.py                # structlog 設定 (27行)
│   ├── models/                       # SQLAlchemy モデル (8テーブル)
│   │   ├── user.py                   #   ユーザー (42行)
│   │   ├── conversation.py           #   会話 (42行)
│   │   ├── message.py                #   メッセージ (35行)
│   │   ├── ticket.py                 #   チケット (66行)
│   │   ├── escalation.py             #   エスカレーション (52行)
│   │   ├── agent_run.py              #   エージェント実行記録 (51行)
│   │   ├── knowledge.py              #   KB記事 + チャンク (47行)
│   │   └── __init__.py               #   全モデル再エクスポート (27行)
│   ├── schemas/                      # Pydantic スキーマ
│   │   ├── auth.py                   #   認証 (39行)
│   │   ├── chat.py                   #   チャット (16行)
│   │   ├── conversation.py           #   会話 (45行)
│   │   ├── ticket.py                 #   チケット (45行)
│   │   ├── escalation.py             #   エスカレーション (33行)
│   │   ├── knowledge.py              #   ナレッジベース (61行)
│   │   └── stats.py                  #   統計 (24行)
│   └── api/                          # REST API ルーター
│       ├── deps.py                   #   DI (get_db, get_current_user) (50行)
│       ├── auth.py                   #   認証 (60行)
│       ├── chat.py                   #   チャット + SSE (137行)
│       ├── conversations.py          #   会話 CRUD (106行)
│       ├── tickets.py                #   チケット CRUD (104行)
│       ├── escalations.py            #   エスカレーション管理 (91行)
│       ├── knowledge.py              #   ナレッジベース CRUD + 検索 (142行)
│       └── stats.py                  #   ダッシュボード統計 (102行)
├── frontend/                         # フロントエンド (React 19)
│   ├── src/
│   │   ├── main.tsx                  # エントリーポイント (14行)
│   │   ├── App.tsx                   # ルーティング (42行)
│   │   ├── api/client.ts             # HTTP クライアント + トークン管理 (70行)
│   │   ├── types/index.ts            # 型定義 (88行)
│   │   ├── hooks/
│   │   │   ├── useAuth.ts            # 認証フック (52行)
│   │   │   └── useSSE.ts             # SSE ストリーミングフック (75行)
│   │   ├── i18n/
│   │   │   ├── config.ts             # i18next 設定 (16行)
│   │   │   ├── ja.ts                 # 日本語翻訳 (70行)
│   │   │   └── en.ts                 # 英語翻訳 (70行)
│   │   ├── constants/colors.ts       # ステータス色マッピング (21行)
│   │   ├── components/Layout.tsx     # サイドバー + メインレイアウト (97行)
│   │   └── pages/
│   │       ├── LoginPage.tsx         # ログイン/登録フォーム (110行)
│   │       ├── DashboardPage.tsx     # KPI + チャート (132行)
│   │       ├── ChatPage.tsx          # リアルタイムチャット (174行)
│   │       ├── TicketsPage.tsx       # チケット一覧 + フィルタ (101行)
│   │       ├── EscalationsPage.tsx   # エスカレーション管理 (124行)
│   │       ├── KnowledgePage.tsx     # ナレッジベース + 検索 (176行)
│   │       ├── AgentFlowPage.tsx     # エージェントフロー図 (117行)
│   │       └── SettingsPage.tsx      # 設定 (54行)
│   ├── index.html                    # HTML テンプレート (12行)
│   ├── package.json                  # 依存関係 (30行)
│   ├── vite.config.ts                # Vite 設定 (15行)
│   └── tsconfig.json                 # TypeScript 設定 (20行)
├── tests/                            # テストスイート (54テスト)
│   ├── test_config.py                # 設定テスト (51行, 8テスト)
│   ├── test_security.py              # セキュリティテスト (49行, 6テスト)
│   ├── test_schemas.py               # スキーマテスト (87行, 19テスト)
│   ├── test_agents.py                # エージェントテスト (131行, 19テスト)
│   └── test_embedding.py             # 埋め込みテスト (38行, 6テスト)
├── alembic/                          # DBマイグレーション
│   ├── env.py                        # 非同期マイグレーション設定 (73行)
│   └── versions/001_initial.py       # 初期スキーマ (151行)
├── scripts/seed.py                   # シードデータ投入 (174行)
├── docker-compose.yml                # PostgreSQL 17 + pgvector (20行)
├── pyproject.toml                    # Python 依存関係 (42行)
├── .env.example                      # 環境変数テンプレート (15行)
└── docs/DESIGN_SPEC.md               # 設計仕様書 (471行)
```

---

## データベース設計

### ER図

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  users   │────<│conversations │────<│ messages │
│          │     │              │     │          │
│ id (PK)  │     │ id (PK)      │     │ id (PK)  │
│ email    │     │ user_id (FK) │     │ conv_id  │
│ password │     │ title        │     │ role     │
│ full_name│     │ status       │     │ content  │
│ role     │     │ metadata_    │     │ metadata_│
│ is_active│     └──────┬───────┘     └──────────┘
└────┬─────┘            │
     │            ┌─────┴──────┐
     │            │            │
┌────▼─────┐ ┌───▼────────┐ ┌─▼───────────┐
│ tickets  │ │escalations │ │ agent_runs  │
│          │ │            │ │             │
│ id (PK)  │ │ id (PK)    │ │ id (PK)     │
│ user_id  │ │ conv_id    │ │ conv_id     │
│ conv_id  │ │ ticket_id  │ │ agent_type  │
│ title    │ │ reason     │ │ input_data  │
│ desc     │ │ sentiment  │ │ output_data │
│ status   │ │ status     │ │ duration_ms │
│ priority │ │ reviewed_by│ │ status      │
│ category │ │ notes      │ │ error_msg   │
│ assigned │ └────────────┘ └─────────────┘
└──────────┘

┌──────────────┐     ┌──────────────┐
│ kb_articles  │────<│  kb_chunks   │
│              │     │              │
│ id (PK)      │     │ id (PK)      │
│ title        │     │ article_id   │
│ content      │     │ content      │
│ category     │     │ embedding    │
│ is_published │     │  (VEC 1536)  │
└──────────────┘     │ chunk_index  │
                     └──────────────┘
```

### テーブル一覧（8テーブル + 8列挙型）

| テーブル | 主な列 | 説明 |
|----------|--------|------|
| users | id, email, hashed_password, full_name, role, is_active | ユーザー管理。3ロール: admin, agent, customer |
| conversations | id, user_id, title, status, metadata_ | チャット会話。ステータス: active, closed, archived |
| messages | id, conversation_id, role, content, metadata_ | 会話内メッセージ。ロール: user, assistant, system |
| tickets | id, user_id, title, description, status, priority, category, assigned_to | サポートチケット。優先度4段階、ステータス4段階 |
| escalations | id, conversation_id, reason, sentiment_score, status, reviewed_by, notes | エスカレーション記録。感情スコア + 承認/却下 |
| agent_runs | id, conversation_id, agent_type, input_data, output_data, duration_ms, status | エージェント実行ログ。6エージェント種別を記録 |
| kb_articles | id, title, content, category, is_published | ナレッジベース記事 |
| kb_chunks | id, article_id, content, embedding (VECTOR 1536), chunk_index | 記事チャンク + pgvector 埋め込み |

---

## API エンドポイント

### 認証

| メソッド | パス | 説明 | 認証 |
|----------|------|------|------|
| POST | `/api/auth/register` | ユーザー登録 | 不要 |
| POST | `/api/auth/login` | ログイン → JWT トークン返却 | 不要 |
| POST | `/api/auth/refresh` | アクセストークン更新 | リフレッシュトークン |
| GET | `/api/auth/me` | ログインユーザー情報取得 | 必要 |

### チャット

| メソッド | パス | 説明 | 認証 |
|----------|------|------|------|
| POST | `/api/chat` | メッセージ送信 → SSE ストリーム応答 | 必要 |
| GET | `/api/chat/{id}/history` | 会話履歴取得 | 必要 |

### 会話

| メソッド | パス | 説明 | 認証 |
|----------|------|------|------|
| GET | `/api/conversations` | 会話一覧（ページネーション + ステータスフィルタ） | 必要 |
| GET | `/api/conversations/{id}` | 会話詳細（メッセージ含む） | 必要 |
| PATCH | `/api/conversations/{id}` | 会話更新 | 必要 |
| DELETE | `/api/conversations/{id}` | 会話削除 | 必要 |

### チケット

| メソッド | パス | 説明 | 認証 |
|----------|------|------|------|
| GET | `/api/tickets` | チケット一覧（顧客は自分のみ） | 必要 |
| POST | `/api/tickets` | チケット作成 | 必要 |
| GET | `/api/tickets/{id}` | チケット詳細 | 必要 |
| PATCH | `/api/tickets/{id}` | チケット更新（顧客はタイトル/説明のみ） | 必要 |

### エスカレーション

| メソッド | パス | 説明 | 認証 |
|----------|------|------|------|
| GET | `/api/escalations` | エスカレーション一覧 | agent/admin |
| GET | `/api/escalations/{id}` | エスカレーション詳細 | agent/admin |
| POST | `/api/escalations/{id}/review` | 承認/却下 | agent/admin |

### ナレッジベース

| メソッド | パス | 説明 | 認証 |
|----------|------|------|------|
| GET | `/api/knowledge` | 記事一覧（公開記事のみ） | 必要 |
| POST | `/api/knowledge` | 記事作成（自動チャンキング + 埋め込み） | agent/admin |
| GET | `/api/knowledge/{id}` | 記事詳細（チャンク含む） | 必要 |
| PATCH | `/api/knowledge/{id}` | 記事更新（内容変更時に再チャンキング） | agent/admin |
| DELETE | `/api/knowledge/{id}` | 記事削除（チャンクもカスケード削除） | agent/admin |
| POST | `/api/knowledge/search` | セマンティック検索 | 必要 |

### 統計

| メソッド | パス | 説明 | 認証 |
|----------|------|------|------|
| GET | `/api/stats` | ダッシュボードKPI | 必要 |
| GET | `/api/stats/agent-performance` | エージェント別実行統計 | 必要 |

### システム

| メソッド | パス | 説明 | 認証 |
|----------|------|------|------|
| GET | `/health` | ヘルスチェック（稼働モード表示） | 不要 |

---

## MCP ツール

FastMCP サーバーが `/mcp` エンドポイントで Streamable HTTP トランスポートを提供。

| ツール名 | パラメータ | 説明 |
|----------|-----------|------|
| `search_knowledge_base` | query, top_k=5 | pgvector コサイン類似度によるセマンティック検索 |
| `create_ticket` | title, description, priority, category, user_id | サポートチケットの作成 |
| `update_ticket` | ticket_id, status, priority, assigned_to | チケットのステータス・優先度・担当者更新 |
| `get_support_metrics` | days=30 | ダッシュボードKPI（会話数・チケット数・解決率） |
| `escalate_to_human` | conversation_id, reason | 人間エージェントへのエスカレーション作成 |

---

## 画面仕様

| 画面 | パス | 機能 |
|------|------|------|
| ログイン | `/login` | メール/パスワードフォーム、登録/ログイン切り替え |
| ダッシュボード | `/` | 6つのKPIカード、エージェント別棒グラフ・円グラフ |
| チャット | `/chat` | 会話サイドバー + SSEリアルタイムストリーミング |
| チケット | `/tickets` | ステータスフィルタ付きチケット一覧 |
| エスカレーション | `/escalations` | 承認/却下アクション付きエスカレーション管理 |
| ナレッジベース | `/knowledge` | 記事一覧 + セマンティック検索 + 記事作成 |
| エージェントフロー | `/agent-flow` | SVGによるエージェントグラフ可視化 |
| 設定 | `/settings` | 言語切り替え（日/英）、動作モード情報 |

---

## セキュリティ設計

| 対策 | 実装 |
|------|------|
| パスワード保護 | bcrypt ハッシュ（自動ソルト生成） |
| 認証トークン | JWT HS256（アクセス: 30分 / リフレッシュ: 7日） |
| トークン検証 | Authorization ヘッダー Bearer トークン + トークンタイプ検証 |
| アクセス制御 | ロールベース（admin/agent/customer）、エンドポイントレベルで適用 |
| データ分離 | 顧客は自身のリソースのみアクセス可能 |
| 入力検証 | Pydantic によるリクエストバリデーション（文字数制限、型チェック） |
| CORS | 許可オリジン制限（設定可能） |

---

## テスト構成

54テスト、5ファイル構成。`pytest` + `pytest-asyncio`（非同期テスト対応）。

| ファイル | テスト数 | 対象 |
|----------|----------|------|
| test_config.py | 8 | デモ/ライブモード検出、URL変換、SSL判定 |
| test_security.py | 6 | bcrypt ハッシュ往復、JWT アクセス/リフレッシュトークン |
| test_schemas.py | 19 | 認証・チケット・ナレッジベーススキーマのバリデーション |
| test_agents.py | 19 | Router 分類、感情分析、チケット抽出、テンプレート応答 |
| test_embedding.py | 6 | 次元数検証、決定論性、値範囲、大文字小文字無視 |

```bash
uv run pytest          # 全テスト実行
uv run pytest -x       # 最初の失敗で停止
```

---

## シードデータ

`scripts/seed.py` により冪等なテストデータ投入が可能。

| データ | 内容 |
|--------|------|
| ユーザー（3名） | admin@example.com（管理者）、agent@example.com（エージェント）、demo@example.com（顧客） |
| KB記事（5件） | 入門ガイド、料金プラン、返品ポリシー、技術要件、アカウントセキュリティ |
| チケット（3件） | パスワードリセット（高優先度/未対応）、二重請求（緊急/対応中）、ダークモード要望（低優先度/解決済み） |
| 会話（1件） | 料金問い合わせ（アクティブ） |

パスワードは環境変数で設定可能: `SEED_ADMIN_PASSWORD`, `SEED_AGENT_PASSWORD`, `SEED_CUSTOMER_PASSWORD`

---

## セットアップ

### 前提条件

- Python 3.12以上
- Node.js 18以上
- Docker（PostgreSQL用）
- uv（Python パッケージマネージャー）

### 手順

```bash
# 1. リポジトリクローン
git clone https://github.com/mer-prog/agent-flow.git
cd agent-flow

# 2. PostgreSQL 起動
docker compose up -d

# 3. 環境変数設定
cp .env.example .env
# .env を編集（JWT_SECRET は必ず変更）

# 4. Python 依存関係インストール
uv sync

# 5. DBマイグレーション実行
alembic upgrade head

# 6. シードデータ投入（任意）
uv run python scripts/seed.py

# 7. バックエンド起動
uv run fastapi dev app/main.py

# 8. フロントエンド起動（別ターミナル）
cd frontend
npm install
npm run dev
```

### 環境変数

| 変数 | 説明 | 必須 |
|------|------|------|
| `DATABASE_URL` | PostgreSQL 接続文字列 | はい |
| `JWT_SECRET` | JWT署名用秘密鍵（HS256） | はい |
| `ANTHROPIC_API_KEY` | Claude API キー（ライブモード用） | いいえ |
| `OPENAI_API_KEY` | OpenAI API キー（ライブモード用） | いいえ |
| `APP_ENV` | 実行環境（development / production） | いいえ |
| `LOG_LEVEL` | ログレベル（デフォルト: INFO） | いいえ |
| `CORS_ORIGINS` | 許可オリジン（JSON配列形式） | いいえ |

---

## 設計判断の根拠

| 判断 | 根拠 |
|------|------|
| LangGraph で StateGraph を採用 | 条件分岐ルーティング、型付き状態管理、エージェントトレースの実装が容易。将来的にチェックポイントやヒューマンインタラプトの追加も可能 |
| デュアルモード（デモ/ライブ） | API キー不要で全機能を動作確認可能にし、開発・デモ・本番の全フェーズに対応 |
| pgvector を採用 | PostgreSQL ネイティブのベクトル検索。別途ベクトルDBを立てる必要がなく、トランザクション整合性も維持 |
| FastMCP で MCP サーバー実装 | Model Context Protocol により外部AIクライアント（Claude Desktop等）からツール呼び出しが可能。エージェントの機能を外部に公開 |
| SSE によるストリーミング | WebSocket より実装がシンプルで、HTTP/2互換。エージェントトレースとトークンの逐次配信に最適 |
| JWT アクセス + リフレッシュトークン | アクセストークン短命（30分）でセキュリティ確保、リフレッシュトークン長命（7日）でUX維持 |
| SHA-256 疑似埋め込み | デモモードで決定論的かつ一貫したベクトルを外部API不要で生成。同じクエリは常に同じベクトルを返す |
| React 19 + Tailwind CSS 4 | 最新のReactフック活用 + ユーティリティファーストCSSでダークテーマを効率的に実装 |
| structlog | 開発時はコンソール出力、本番時はJSON構造化ログ。環境による自動切り替え |

---

## 運用コスト

| サービス | プラン | 月額 |
|----------|--------|------|
| Render | Free (Web Service) | $0 |
| Neon | Free (PostgreSQL + pgvector) | $0 |
| Claude API（ライブモード） | 従量課金 | ~$0.01〜0.05 / メッセージ |
| OpenAI API（ライブモード） | 従量課金 | ~$0.001 / 埋め込みリクエスト |
| **合計（デモモード）** | | **$0** |

---

## 作者

[@mer-prog](https://github.com/mer-prog)
