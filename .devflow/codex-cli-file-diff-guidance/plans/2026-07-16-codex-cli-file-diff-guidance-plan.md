# Codex CLI 文件变更展示规范实施计划

> **给智能代理工作者：** 实施时需逐项执行，并以复选框记录进度。

**目标：** 通过 `AGENTS.md` 约束，让常规文本编辑优先走补丁编辑（apply_patch），从而提高 Codex CLI 展示 `Added` / `Edited` 内联差异的概率。

**方案：** 在现有“工具约束”章节中增加一个专门小节，仅约束仓库内文本文件的编辑方式；同时为生成、二进制和批量工具保留 Shell（命令行）例外，并要求例外后展示目标文件的 Git 差异（git diff）。

**技术栈：** Markdown、Codex CLI、Git。

---

### 任务 1：补充文件变更展示约束

**文件：**
- 修改：`AGENTS.md`
- 验证：`git diff --check`

- [x] **步骤 1：新增“文件编辑与变更展示”小节**

在 `## 工具约束` 下新增三级标题，并写明以下规则：

```markdown
### 文件编辑与变更展示

1. 修改仓库内可追踪的文本文件时，优先使用补丁编辑（apply_patch）。
2. 普通编辑不得使用 `Set-Content`、`Add-Content`、`echo`、重定向等 Shell（命令行）写入方式替代补丁编辑。
3. 生成文件、二进制文件或批量工具无法替代时可使用 Shell 写入；完成后必须展示 `git diff -- <相对路径>`，并说明这类写入不保证 Codex CLI 渲染 `Added` / `Edited`。
```

- [x] **步骤 2：检查 Markdown 与补丁完整性**

运行：

```powershell
git diff --check -- AGENTS.md
git diff -- AGENTS.md
```

预期：命令成功；差异仅包含新增的小节，且不存在空白错误。

- [x] **步骤 3：提交（commit）相关文件**

用户在收尾指令中已明确授权提交；仅暂存 `AGENTS.md` 和 `.devflow/codex-cli-file-diff-guidance/` 下的文件，不纳入其他 mission 或既有工作区改动。

## 自检

- 需求覆盖：任务 1 同时覆盖补丁编辑优先、Shell 例外与差异展示要求。
- 占位符扫描：无 `TODO`、`TBD` 或未定义步骤。
- 一致性：所有文件路径均为相对路径。
