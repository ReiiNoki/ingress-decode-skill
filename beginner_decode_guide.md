# Ingress Passcode Decode 新手指南

这是一张学习路线图，不重复算法手册。目标是帮助你知道先读什么、什么时候查哪份资料，
以及如何判断一次解码是否可信。

## 1. 先理解目标

Decode 不是把密文丢进工具后挑一个顺眼的输出，而是持续完成这个循环：

```text
观察题面 → 提出有依据的假设 → 执行变换 → 验证输出 → 判断是否进入下一层
```

最终结果通常包含可解释的 keyword、数字和校验片段，但格式会随来源和时期变化。
具体格式只在 [Passcode 格式与线索识别](references/passcode-format.md) 中维护。

## 2. 第一次解题

按以下顺序完成一题：

1. 打开 [通用解密流程](references/workflow.md)，用其中的记录模板保存原始题面。
2. 根据字符、分组、标题、图片和异常符号形成第一批假设。
3. 在 [经典密码算法详解](references/cipher-patterns.md) 中只查与当前特征匹配的章节。
4. 如果题面包含图片、动画、二维码、颜色或地图，按
   [图片与外部线索检查指南](references/image-clues.md) 保存和检查原始证据。
5. 基础变换较多时运行：

   ```powershell
   python scripts/quick_decode.py "<密文>"
   ```

6. 对照 [Passcode 格式与线索识别](references/passcode-format.md) 检查 keyword 和每个片段的来源。
7. 卡住时回到 [通用解密流程](references/workflow.md) 的排错清单，不要无记录地重复尝试。
8. 完成后再看 [实战案例复盘](references/examples.md)，比较自己遗漏的线索和验证步骤。

工具输出只是候选。即使出现可读英文，也可能只是下一层提示；即使字符串符合格式，
也可能是巧合或依赖未经验证的猜测。

## 3. 文档地图

| 你的问题 | 阅读位置 |
| --- | --- |
| 应该先做什么、卡住怎么排查？ | [通用解密流程](references/workflow.md) |
| 这种字符可能是什么算法？ | [经典密码算法详解](references/cipher-patterns.md) |
| 图片、二维码、颜色或地图应怎样检查？ | [图片与外部线索检查指南](references/image-clues.md) |
| 结果是否像 passcode，keyword 是否合理？ | [Passcode 格式与线索识别](references/passcode-format.md) |
| 想看一题怎样完整复盘？ | [实战案例复盘](references/examples.md) |
| 想批量尝试基础变换？ | `scripts/quick_decode.py` |

## 4. 学习路线

### 4.1 建立格式感

先阅读 `references/passcode-format.md`。练习区分最终 passcode、keyword、中间提示和普通英文。

### 4.2 掌握基础转换

按 `references/cipher-patterns.md` 的顺序学习 Atbash、ROT、Base64、ASCII/Hex/Binary 和 Morse。
每种算法至少手算一个短例子，再用脚本核对。

### 4.3 训练观察力

练习从标题、文件名、排版、键盘位置、图片和地图中找线索。不要在记录题面前清理标点、
空格或换行，因为它们可能就是分组信息。

### 4.4 处理多层题

每一层都记录“为什么尝试、得到什么、它更像答案还是下一层提示”。只有当最终各片段均可解释，
且不存在关键未用线索时，才提高结论可信度。

## 5. 练习方法

每次选择一个来源案例时：

1. 先只看题面并写下观察。
2. 按 `workflow.md` 记录尝试，不提前看答案。
3. 查看来源解法后独立复算每一步。
4. 标出无法复现、依赖猜测或不符合标准码表的部分。
5. 用自己的话复述完整链路，并给结论标注可信度。

来源文章也可能出错。`references/examples.md` 中的案例状态用于区分可复现内容与来源声称，
不要为了得到既定答案而放宽算术或编码规则。

## 6. 延伸阅读

可以在 [bjres.net](https://bjres.net) 搜索 Passcode 基础格式、Morse、Base64、keyword、
键盘线索和多层组合题。阅读时继续使用同一套记录与验证方法。
