# Mem0 API Patches

这个目录包含对 Mem0 API 的补丁文件，用于在不修改 `projects/mem0` 目录的情况下应用自定义修改。

## 补丁列表

### cors.patch
添加 CORS 支持，允许前端从不同源访问 API。

**修改内容**：
- 导入 `CORSMiddleware`
- 添加 CORS 配置，支持通过环境变量 `CORS_ORIGINS` 配置允许的源

**应用方式**：
在 Dockerfile 构建时自动应用。

## 如何创建新补丁

1. **修改源文件**（临时）：
   ```bash
   # 在 projects/mem0/server/main.py 中做修改
   ```

2. **生成补丁**：
   ```bash
   cd projects/mem0/server
   # 创建原始文件的备份
   cp main.py main.py.orig
   
   # 做修改...
   
   # 生成补丁
   diff -u main.py.orig main.py > ../../../deployment/mem0/patches/your-patch.patch
   ```

3. **恢复源文件**：
   ```bash
   # 恢复原始文件
   mv main.py.orig main.py
   # 或者从 Git 恢复
   git checkout projects/mem0/server/main.py
   ```

4. **更新 Dockerfile**：
   在 Dockerfile 中添加应用补丁的步骤：
   ```dockerfile
   COPY deployment/mem0/patches/your-patch.patch /tmp/your-patch.patch
   RUN cd /app && patch -p0 < /tmp/your-patch.patch || (echo "Warning: Patch failed" && true)
   ```

## 补丁格式说明

补丁文件使用标准的 unified diff 格式：
- `--- a/main.py`：原始文件
- `+++ b/main.py`：修改后的文件
- `@@ -行号,行数 +行号,行数 @@`：修改位置
- `-`：删除的行
- `+`：添加的行
- 没有前缀：未修改的行（上下文）

## 注意事项

1. **不要直接修改 `projects/mem0` 目录**：这些是引用的外部项目，应该保持原始状态
2. **补丁路径**：由于 Dockerfile 中复制了 `projects/mem0/server/` 到 `/app`，补丁文件中的路径应该是 `main.py`（不是 `projects/mem0/server/main.py`）
3. **补丁失败处理**：Dockerfile 中使用 `|| true` 确保补丁失败不会中断构建，但会输出警告
4. **测试补丁**：在应用补丁前，可以在本地测试：
   ```bash
   cd /path/to/projects/mem0/server
   patch -p0 < /path/to/deployment/mem0/patches/cors.patch
   ```

## 当前补丁状态

- ✅ `cors.patch`：已创建并配置，在 Dockerfile 中自动应用

