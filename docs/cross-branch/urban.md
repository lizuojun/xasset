# xasset-urban 分支同步事项

---

### [仅通知] SceneRegion 新增 category 字段

- **发出方**：xasset-urban
- **接收方**：all
- **日期**：2026-04-14
- **内容**：
  为支持 urban/outdoor 等多场景类型复用理解层数据结构，
  `xasset/pipeline/stages/scene_understand.py` 中的 `SceneRegion` 新增一个字段：

  ```python
  category: str = "room"   # 默认值 "room"，house 场景无需修改
  ```

  该改动完全向后兼容，house 场景所有代码、测试均无需变更。
  urban 场景使用时传入 `"building"` / `"road"` / `"open_space"` 等值。

- **是否需要处理**：否（仅通知）
- **说明**：此字段改动将随 urban 分支 PR 一并合入 master，其他分支 merge 或 cherry-pick 后自动获得。
