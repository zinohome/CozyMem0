# 强制覆盖本地更改指南

当本地有未提交的更改，但想用 GitHub 上的代码强制覆盖时，可以使用以下方法。

## 方法 1：使用脚本（推荐）

```bash
cd /data/build/CozyMem0
./deployment/mem0/force-pull.sh
```

脚本会：
1. 检查本地是否有未提交的更改
2. 询问确认
3. 获取最新的远程代码
4. 强制重置到远程分支
5. 可选清理未跟踪的文件

## 方法 2：手动命令（快速）

### 2.1 简单重置（推荐）

```bash
cd /data/build/CozyMem0

# 获取最新代码
git fetch origin

# 强制重置到远程 main 分支
git reset --hard origin/main
```

### 2.2 完整重置（包括清理未跟踪文件）

```bash
cd /data/build/CozyMem0

# 获取最新代码
git fetch origin

# 强制重置到远程 main 分支
git reset --hard origin/main

# 清理未跟踪的文件和目录（谨慎使用！）
git clean -fd
```

## 方法 3：丢弃特定文件的更改

如果只想丢弃特定文件的更改：

```bash
cd /data/build/CozyMem0

# 丢弃特定文件的更改
git checkout -- deployment/mem0/webui.Dockerfile

# 然后正常拉取
git pull
```

## 方法 4：暂存本地更改（保留备份）

如果想保留本地更改作为备份：

```bash
cd /data/build/CozyMem0

# 暂存本地更改
git stash

# 拉取远程代码
git pull

# 如果需要恢复本地更改（可选）
# git stash pop
```

## 注意事项

⚠️ **警告**：
- `git reset --hard` 会**永久删除**所有未提交的本地更改
- `git clean -fd` 会**永久删除**所有未跟踪的文件和目录
- 执行前请确保不需要保留这些更改

## 验证

执行后验证：

```bash
# 检查状态
git status

# 应该显示：
# On branch main
# Your branch is up to date with 'origin/main'.
# nothing to commit, working tree clean
```

## 常见问题

### Q: 如何只覆盖特定文件？

A: 使用 `git checkout`：
```bash
git checkout origin/main -- deployment/mem0/webui.Dockerfile
```

### Q: 如何查看本地和远程的差异？

A: 使用 `git diff`：
```bash
# 查看本地和远程的差异
git diff HEAD origin/main

# 查看特定文件的差异
git diff HEAD origin/main -- deployment/mem0/webui.Dockerfile
```

### Q: 如何备份本地更改？

A: 使用 `git stash` 或创建补丁：
```bash
# 方法 1: 使用 stash
git stash save "backup before force pull"

# 方法 2: 创建补丁文件
git diff > local-changes.patch
```

