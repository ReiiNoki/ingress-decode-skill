# Passcode 格式与线索识别

---

## 1. Passcode 基础

### 1.1 什么是 Passcode

Ingress 官方（玩家称"猩猩"）通过 Investigation Blog、Ingress Report 视频、WOTD 网站、社交媒体等渠道发布的兑换码。玩家破解密文后获得 passcode，可在游戏 Scanner 中兑换物品（XM、Resonator、Portal Key、AP 等）。

### 1.2 常见 Passcode 格式

下表来自归档基础篇所记录的 2016 年历史规则（`#` 表示数字，`x` 表示字母）。它适合分析
同一时期的旧题，不保证适用于后来活动或当前 passcode：

| 来源 | 格式 | 数字范围 |
|------|------|----------|
| Investigation Blog | `xxx##keyword###xx` | # 为 2-9 |
| WOTD (jojoingresswotd.github.io) | `x#x#keywordx#xx` | # 为 0-9 |
| Ingress Report (forever code) | `keyword#xx##xx#` | # 为 0-9 |
| Anomaly 活动 | `xxxxxxxx#keyword#` | # 为 2-9 |
| Old formats | `#xxx#keywordx#x#x` | # 为 2-9 |

**keyword** 是 passcode 的核心可读部分，通常是 Ingress 相关词汇（人物名、物品名、地名、事件名等）。

### 1.3 把格式当作 crib，而不是答案

归档文章经常先按预期格式定位数字位和 keyword 区，再分别变换。例如：

- 变换保持数字位置，只对字母做 Atbash 或 ROT。
- Hex 字节在预期数字位置有共同高位，据此识别 Hex Atbash。
- 英文数字只露出前缀或后缀，按应为数字的位置补全。
- 一个长串中数字数量正好对应一个或多个历史格式。

这种方法可以缩小搜索空间，但有确认偏差风险。使用时同时保留：

1. 原始字符与未经格式约束的转换结果。
2. 假设的来源类型和格式模板。
3. 每个切分边界的依据。
4. 至少一个独立证据，例如标准解码、标题提示、keyword 来源或同组 code 规则。

不能因为字符串能被切成 `xxx##word###xx` 就认定 `word` 是 keyword。

### 1.4 判断结果是否像 Passcode

- 字母与数字交替出现，有规律分段
- 包含一个可识别的英文 keyword
- keyword 能被题面/图片/Ingress lore 解释
- 每段结果都有来源，而非硬凑
- **反例**：一个普通英文单词没有数字搭配 → 可能只是中间线索

### 1.5 Passcode 来源渠道

- Investigation Blog 页面 HTML 中（F12 开发者工具可查）
- 题图的 `alt` 属性、HTML class 等隐藏位置
- Ingress Report 视频画面（特定时间帧）
- jojoingresswotd.github.io 及其 GitHub repo
- 官方社交媒体帖子

---

## 2. Keyword 识别

### 2.1 常见 Keyword 来源

| 类别 | 示例 |
|------|------|
| Ingress 人物 | Jarvis, Hank, Devra, Misty, Susanna, Yuri, Roland, ADA |
| 阵营与组织 | Enlightened, Resistance, Niantic, IQTech, Visur, Hulong |
| Ingress 物品/概念 | Portal, XM, Resonator, Shard, Glyph, Scanner, Capsule |
| 地点/事件 | Anomaly, MissionDay, Obsidian, Recursion, ViaLux |
| 解码中间结果 | 某层解码后出现的英文词 |
| 标题/文件名 | 标题里的异常词、谐音、错别字 |
| 图片隐藏信息 | 图片文字、文件名、alt 文本 |
| 同组其他 code | 数字 key、分隔符、keyword、读取方向或预期 code 数量 |

### 2.2 判断 Keyword 是否靠谱

一个靠谱的 keyword 通常满足：

- 能和数字部分拼成 passcode
- 与题面主题有关
- 能解释标题或图片里的关键线索
- 大小写、单复数、拼写能被合理解释

> 不要因为某个词"看起来像 Ingress"就直接当答案。好的答案应该能讲清楚它从哪里来。

### 2.3 Keyword 列表参考

ingresscodes 团队维护了一份 keyword 列表：
<https://github.com/ingresscodes/>

---

## 3. 图片与外部线索

### 3.1 图片、文件、地图和页面

遇到图片、动画、二维码、颜色、坐标、地图或 HTML 隐藏信息时，按
`image-clues.md` 的顺序检查并记录证据。本文件只负责判断这些信息能否支持 keyword
或 passcode 片段，不重复图像和外部线索的提取步骤。

### 3.2 Ingress Lore 线索

常见 keyword 可能来自：

- 人物名：Jarvis, Hank, Devra, Misty, Susanna, Roland, Yuri, ADA
- 阵营与组织：Enlightened, Resistance, Niantic, IQTech
- XM, Portal, Resonator, Key, Shard, Glyph, Scanner
- 官方事件：Anomaly, Mission Day, 碎片（Shard）活动
- Investigate 中出现过的名词
- 游戏内历史人物关系

---

## 4. 相关资源

| 资源 | 用途 |
|------|------|
| **[bjres.net](https://bjres.net)** | 教程文章的原始来源和线上上下文 |
| **[ingress.codes](https://ingress.codes)** | passcode 格式与 keyword 列表 |
| **[ingresscodes GitHub](https://github.com/ingresscodes/)** | keyword 列表仓库 |
| **[jojoingresswotd.github.io](https://jojoingresswotd.github.io)** | WOTD passcode 来源 |
| **Investigation Blog** | 主要 passcode 发布渠道 |
| **Ingress Report** | 视频中的 passcode |
| **标准 ITU 摩斯电码表** | Morse 解码必备 |
| **国际标准盲文对照表** | Braille 解码必备 |
