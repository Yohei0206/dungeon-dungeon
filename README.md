# dungeon-dungeon

2DすごろくゲームのAI決定ロジックを簡易的にまとめています。

## 追加済みの決定ロジック
- **職業別の優先度**: Warrior/Hunter/Cleric/Rogue/Mage に対して探索・戦闘・経済の優先度を付与しました。
- **移動選択**: 視界に入るタイルを対象に、距離ヒューリスティックと価値・危険度を組み合わせて移動先を算出します。
- **リスク評価と安全行動**: HP残量・罠確率・逃走成功率からリスクを数値化し、特に Hunter/Cleric は閾値を下げて撤退・回復を優先します。

`dungeon_ai.agent.AgentDecisionMaker` に主要なロジックがあります。`python -m unittest` でシナリオテストを確認できます。
