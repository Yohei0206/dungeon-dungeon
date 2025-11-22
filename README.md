# dungeon-dungeon

2D すごろくゲームのための進行・ネット対戦コア。下記の 3 つのコンポーネントでターン管理と同期を分離して設計しています。

## GameManager

- 30 ターン固定の進行を管理し、ターンごとに VP (Victory Point) を集計。
- ターン中のコマンド投入 (`enqueue_commands` / `receive_remote_commands`) と解決 (`resolve_current_turn`) をまとめて制御。
- `NetSession`・`TurnController` を束ね、オフラインテスト用に `run_full_game` も提供。

## TurnController

- プレイヤー順序に基づいて入力キューを保持し、各ターンの行動解決を担当。
- 実際の行動処理は `action_resolver` コールバックに委譲するため、ゲームロジックを差し替えやすい。

## NetSession

- Lockstep 前提のネット対戦で、入力コマンドの送受信とターンごとのリプレイ検証を分離。
- 受信済みコマンドをプレイヤー順に整列し、`replay_log` で検証可能な履歴を保持。
