# ingress-decode-skill

参考 bjres.net Ingress Passcode 解迷教程整理的解密技能包，包含知识库、
经过状态标注的案例和可直接运行的解码工具箱。

> 既可安装为 Codex Skill，也可作为玩家自学手册。

---

## 1. 目录结构

```text
ingress-decode-skill/
├── SKILL.md                          ← Codex Skill 入口
├── README.md                         ← 项目与安装说明
├── beginner_decode_guide.md          ← 新手入门指南
├── references/                       ← Skill 按需读取的领域知识
│   ├── workflow.md
│   ├── cipher-patterns.md
│   ├── image-clues.md
│   ├── passcode-format.md
│   └── examples.md
└── scripts/
    └── quick_decode.py               ← 本地解码工具箱
```

---

## 2. 快速开始

### 2.1 一键扫描密文

```powershell
python scripts/quick_decode.py "cbt33nzplgl878iw"
```

要求 Python 3.9 或更高版本；快速解码工具仅使用标准库。命令会输出 Reverse、Atbash、
ROT、键盘偏移、Base64、矩阵重排等候选结果。候选结果仍需根据题面和格式验证。

### 2.2 运行内置示例

```powershell
python scripts/quick_decode.py
```

展示工具用法和内置示例。归档来源存在疑点的案例会在 `references/examples.md` 中标明状态，
不应仅凭来源文章视为已验证答案。

### 2.3 阅读知识库

新手先阅读 `beginner_decode_guide.md`。实际解题时再按需查阅：

- `references/workflow.md` — 解题步骤、排错清单和记录模板
- `references/cipher-patterns.md` — 算法特征与具体变换
- `references/image-clues.md` — 图片、元数据、颜色、动画、地图与页面检查
- `references/passcode-format.md` — passcode、keyword 与外部线索
- `references/examples.md` — 完整案例、验证状态与复盘

---

## 3. 安装为 Codex Skill

Codex 通过 `SKILL.md` 的 `name` 和 `description` 判断何时加载 Skill，不依赖特殊文件后缀。
将 Skill 必需文件复制到 `$CODEX_HOME/skills/ingress-decode`；未设置 `CODEX_HOME` 时，
默认目录是 `~/.codex/skills/ingress-decode`。

在仓库根目录运行：

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$target = Join-Path $codexHome "skills\ingress-decode"
New-Item -ItemType Directory -Force $target | Out-Null
Copy-Item -Path .\SKILL.md, .\references, .\scripts -Destination $target -Recurse -Force
```

重新启动或刷新 Codex 后，可以直接说“用 ingress-decode 分析这段 Ingress 密文”，
也可以自然描述解码任务，由 description 触发 Skill。

其他 AI 助手的 Skill/Instructions 格式并不统一。若要适配其他客户端，应按该客户端的
官方目录和触发机制转换；本项目不再把 `applyTo` 声明成通用标准。

子文件引用关系：

```
SKILL.md（入口）
├── → references/workflow.md         解题流程和排错
├── → references/cipher-patterns.md  密码算法详解
├── → references/passcode-format.md  格式与线索
├── → references/examples.md         案例复盘
└── → scripts/quick_decode.py        Python 工具
```

---

## 4. 解码工具速查

| 函数                                                         | 说明                         |
| ------------------------------------------------------------ | ---------------------------- |
| `atbash(s)`                                                | 字母前后对折                 |
| `rot(s, n)` / `rot13(s)` / `rot5(s)`                   | Caesar 移位系列              |
| `decode_base64(s)`                                         | Base64（自动补 pad）         |
| `decode_hex(s)` / `decode_binary(s)` / `a1z26(s)`      | Hex / Binary / A1Z26         |
| `decode_morse(s)` / `keyboard_row_to_morse(s)`           | Morse 解码 / 键盘行 Morse    |
| `keyboard_shift(s, direction)`                             | QWERTY 左移 / 右移 / 镜像    |
| `read_rows_bottom_up(s, cols)` / `read_columns(s, cols)` | 矩阵重排                     |
| `decode_rail_fence(s, rails)`                              | 栅栏密码                     |
| `braille_to_text(s)` / `braille_multiply_dots(text)`     | 盲文转字母 / 点数运算        |
| `guess_encoding(s)`                                        | 自动识别密文编码类型         |
| `scan_all(s)`                                              | **一键跑全部基础变换** |

---

## 5. License

本仓库中由项目作者原创的代码和文档采用 [MIT License](LICENSE)。

引用或链接的第三方文章、图片、商标、游戏素材及其他内容不属于本许可证授权范围，
其权利归原权利人所有。案例出处尽量链接至原页面。
