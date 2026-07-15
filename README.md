# ingress-decode-skill

参考 bjres.net Ingress Passcode 解迷教程提炼的解密技能包，包含自足的知识库、
经过状态标注的精选案例和可直接运行的解码工具箱。运行时不依赖原始文章归档。

> 既可安装为 Codex Skill，也可作为玩家自学手册。

---

## 核心能力

- 按“观察、假设、变换、验证”的流程分析题面，而不是从工具输出中挑一个像答案的结果。
- 覆盖常见经典密码、文本编码、键盘映射、矩阵重排、电话键盘、游程编码和多层组合题。
- 处理图片、二维码、颜色、动画、地图、HTML 隐藏信息以及多个 code 之间的依赖关系。
- 用历史 passcode 格式辅助分段，同时保留独立证据，降低按预期格式硬凑答案的风险。
- 只携带提炼后的知识、精选案例和确定性工具，不读取或分发完整文章归档。

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
├── scripts/
│   └── quick_decode.py               ← 本地解码工具箱
└── tests/
    └── test_quick_decode.py          ← 解码函数回归测试
```

---

## 2. 快速开始

### 2.1 一键扫描密文

```powershell
python scripts/quick_decode.py "cbt33nzplgl878iw"
```

要求 Python 3.9 或更高版本；快速解码工具仅使用标准库。命令会输出 Reverse、Atbash、
ROT、键盘偏移、Base32/Base64/Base85、数值编码和矩阵重排等候选结果。候选结果仍需根据
题面和格式验证。

`scan_all()` 适合发现基础变换候选。Vigenere、AutoKey、Gronsfeld 和 XOR 等需要密钥的算法，
仍应结合题面线索单独调用对应函数，避免没有依据地穷举。

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

### 2.4 隐私与发布

如果使用配套爬虫在本机生成了原始文章、图片和索引，它们只保存在根目录的 `output/` 中。
该目录已被 `.gitignore` 排除，公开仓库中的 Skill 运行时也不会读取它。发布到 GitHub 时
只提交本页目录结构中列出的知识库、工具和测试即可，不需要上传完整文章，也不需要在解题时
做全量搜索。

使用 Git 提交前可运行 `git status --ignored`，确认 `output/` 显示为 ignored。若通过网页
手动上传文件，`.gitignore` 不会代替你过滤文件，请不要选择 `output/`。

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
└── → scripts/quick_decode.py        Python 解码工具
```

---

## 4. 解码工具速查

| 函数                                                         | 说明                         |
| ------------------------------------------------------------ | ---------------------------- |
| `atbash(s)`                                                | 字母前后对折                 |
| `rot(s, n)` / `rot13(s)` / `rot5(s)`                   | Caesar 移位系列              |
| `decode_base64(s)`                                         | Base64（自动补 pad）         |
| `decode_base32(s)` / `decode_base85(s)`                    | Base32 / Base85              |
| `decode_uu_line(s)` / `xor_hex_with_text(s, key)`          | UUencode / XOR               |
| `decode_hex(s)` / `decode_binary(s)` / `a1z26(s)`      | Hex / Binary / A1Z26         |
| `decode_morse(s)` / `keyboard_row_to_morse(s)`           | Morse 解码 / 键盘行 Morse    |
| `keyboard_shift(s, direction)`                             | QWERTY 左移 / 右移 / 镜像    |
| `read_rows_bottom_up(s, cols)` / `read_columns(s, cols)` | 矩阵重排                     |
| `decode_rail_fence(s, rails)`                              | 栅栏密码                     |
| `gronsfeld(s, numeric_key)`                                | 数字密钥逐位 Caesar          |
| `vigenere(s, key)` / `autokey_plaintext(s, key)`           | Vigenere / 明文 AutoKey      |
| `decode_multitap_pairs(s)` / `decode_multitap_runs(s)`     | 电话键盘编码                 |
| `decode_alternating_run_lengths(s)`                        | 交替 0/1 游程解码            |
| `braille_to_text(s)` / `braille_multiply_dots(text)`     | 盲文转字母 / 点数运算        |
| `character_profile(s)`                                     | 字符类别、长度与因数概况     |
| `guess_encoding(s)`                                        | 自动识别密文编码类型         |
| `scan_all(s)`                                              | **一键跑全部基础变换** |

---

## 5. 验证

工具箱只使用 Python 标准库。提交修改前运行：

```powershell
python -m unittest discover -s tests -v
python -m py_compile scripts\quick_decode.py
```

测试覆盖典型归档案例、标准密码示例和曾经容易出错的边界行为。测试通过只说明函数实现符合
既定规则，不代表任意候选结果都是正确 passcode；最终仍需按 `references/workflow.md` 验证。

---

## 6. License

本仓库中由项目作者原创的代码和文档采用 [MIT License](LICENSE)。

引用或链接的第三方文章、图片、商标、游戏素材及其他内容不属于本许可证授权范围，
其权利归原权利人所有。案例出处尽量链接至原页面。
