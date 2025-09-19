# 🤝 贡献指南 - O-Red

感谢您有兴趣为 O-Red 做出贡献！这个项目依靠热情贡献者的社区繁荣，他们与我们共同致力于构建一个去中心化且有伦理的网络。

## 🌟 如何贡献

无论您的经验如何，都有很多方式可以为 O-Red 做出贡献：

### 🔧 开发
- 修复 Bug
- 添加新功能
- 提升性能
- 重构现有代码
- 编写测试

### 📚 文档
- 改进现有文档
- 编写教程
- 翻译成其他语言
- 修正错别字
- 添加代码示例

### 🎨 设计与 UX
- 改进用户界面
- 设计原型
- 优化用户体验
- 设计图标与视觉元素

### 🔒 安全
- 识别漏洞
- 进行安全审计
- 提出安全改进建议
- 测试系统稳健性

### 🌍 社区
- 帮助新用户
- 回答论坛问题
- 组织活动
- 宣传项目

## 🚀 快速开始

### 1. Fork 并克隆

```bash
# 在 GitHub 上 fork 仓库，然后克隆你的 fork
git clone https://github.com/YOUR_USERNAME/O-Red.git
cd O-Red

# 添加原始仓库为 remote
git remote add upstream https://github.com/OriginalOwner/O-Red.git
```

### 2. 设置开发环境

```bash
# 按安装指南操作
cd implementation
# 详见 GUIDE_TEST_LOCAL.md
```

### 3. 创建分支

```bash
# 为你的贡献创建分支
git checkout -b feature/my-new-feature
# 或
git checkout -b fix/bug-fix
# 或
git checkout -b docs/improve-documentation
```

## 📋 贡献类型

### 🐛 提交 Bug 报告

在提交 Bug 前：
1. 检查是否已在 [Issues](https://github.com/[USERNAME]/O-Red/issues) 中报告
2. 使用最新代码进行测试
3. 准备可复现示例

**Bug 报告模板：**

```markdown
## Bug 描述
清晰简洁的问题描述。

## 重现步骤
1. 转到 '...'
2. 点击 '...'
3. 滚动到 '...'
4. 看到错误

## 期望行为
对应发生的正确情况的清晰描述。

## 截图
如适用，请添加截图。

## 环境
- 操作系统: [例如 Ubuntu 20.04]
- 浏览器: [例如 Chrome 94]
- Python 版本: [例如 3.9.7]
- Node.js 版本: [例如 16.14.0]

## 附加信息
关于问题的其他信息。
```

### ✨ 提议功能

**功能请求模板：**

```markdown
## 功能概要
对请求功能的清晰简洁描述。

## 动机
为什么该功能有用？它解决了什么问题？

## 详细描述
对建议功能的详细说明。

## 考虑的替代方案
你考虑过哪些替代方案？

## 建议的实现
如果你有实现想法，请在这里分享。
```

## 🔄 贡献流程

### 1. 开发

```bash
# 保持你的分支为最新
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/my-new-feature
git rebase main

# 完成变更
# ...

# 添加并提交
git add .
git commit -m "feat: 添加新功能 X"
```

### 2. 测试

确保所有测试通过：

```bash
# API 测试
cd central-api
python -m pytest app/tests/ -v

# 前端测试
cd ../web-interface
npm test

# P2P 测试
cd ../node-client
python -m pytest tests/ -v
```

### 3. 代码格式化

我们使用自动格式化工具：

```bash
# Python（API 和 Node Client）
pip install black isort
black .
isort .

# JavaScript/TypeScript（Web 界面）
npm run lint
npm run format
```

### 4. 提交规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更改
- `style`: 不影响代码的更改（空格、格式化等）
- `refactor`: 不修复 Bug 也不新增功能的代码更改
- `perf`: 提升性能的代码更改
- `test`: 添加或修复测试
- `chore`: 构建工具或辅助库的更改

**示例：**
```bash
git commit -m "feat(api): add node management endpoint"
git commit -m "fix(ui): fix mobile display bug"
git commit -m "docs: update installation guide"
git commit -m "test(p2p): add tests for peer discovery"
```

### 5. Pull Request

```bash
# 推送你的分支
git push origin feature/my-new-feature

# 在 GitHub 上打开 Pull Request
```

**Pull Request 模板：**

```markdown
## 描述
清晰描述此 PR 的功能。

## 变更类型
- [ ] Bug 修复（修复问题的更改）
- [ ] 新功能（新增功能的更改）
- [ ] 破坏性更改（会破坏现有功能的修正或功能）
- [ ] 此更改需要更新文档

## 测试
- [ ] 我已在本地测试我的更改
- [ ] 我已添加测试以证明我的修复有效或我的功能可用
- [ ] 新旧单元测试在我的更改下均通过

## 检查表
- [ ] 我的代码遵循项目的风格指南
- [ ] 我已对代码进行自检
- [ ] 我已对代码进行注释，特别是在难以理解的区域
- [ ] 我已对文档进行相应更改
- [ ] 我的更改不会产生新的警告
```

## 📐 代码标准

...（其余与英文版本一致）...
