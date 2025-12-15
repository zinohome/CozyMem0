# 用户选择器功能

## 功能概述

添加了用户选择器功能，允许用户在 WebUI 界面中直接选择或输入用户 ID，而无需修改环境变量。

## 功能特性

### 1. **Navbar 用户选择器**

在导航栏右侧添加了用户选择器按钮，显示当前用户 ID，点击可以：
- 查看当前用户
- 输入新的用户 ID
- 快速选择常用用户
- 查看最近使用的用户

### 2. **Settings 页面用户选择**

在设置页面顶部也添加了用户选择器，方便在设置页面切换用户。

### 3. **本地存储**

- 用户选择会自动保存到 `localStorage`
- 最近使用的用户列表也会保存（最多5个）
- 刷新页面后用户选择不会丢失

### 4. **Redux 集成**

- 用户 ID 存储在 Redux store 中
- 所有 API 调用自动使用当前选择的用户 ID
- 切换用户后，所有记忆数据会自动刷新

## 使用方法

### 在 Navbar 中切换用户

1. 点击导航栏右侧的用户选择器按钮（显示当前用户 ID）
2. 在弹出的菜单中选择：
   - **输入新用户 ID**：在输入框中输入新的用户 ID，点击 "Apply"
   - **快速选择**：点击常用用户或最近使用的用户按钮

### 在 Settings 页面切换用户

1. 进入 Settings 页面
2. 在页面顶部找到用户选择器
3. 按照上述方法切换用户

## 技术实现

### 新增文件

1. **`components/UserSelector.tsx`**
   - 用户选择器组件
   - 支持输入和快速选择
   - 集成 localStorage 持久化

### 修改文件

1. **`store/profileSlice.ts`**
   - 添加从 localStorage 读取用户 ID 的逻辑
   - 更新 `setUserId` action 以保存到 localStorage

2. **`components/Navbar.tsx`**
   - 添加用户选择器组件

3. **`app/settings/page.tsx`**
   - 添加用户选择器组件

## 补丁文件

所有更改通过补丁文件应用：
- `deployment/mem0/webui-patches/user-selector.patch`

## 构建和部署

### 应用补丁

补丁会在构建 WebUI 镜像时自动应用（在 `webui.Dockerfile` 中）。

### 重新构建 WebUI

```bash
cd /data/build/CozyMem0/deployment/mem0
./build-webui.sh
```

## 用户体验

### 优势

1. **无需重启容器**：切换用户不需要修改环境变量和重启容器
2. **即时生效**：切换用户后，所有 API 调用立即使用新用户 ID
3. **持久化**：用户选择保存在浏览器中，刷新后不会丢失
4. **便捷**：支持快速选择和输入，操作简单

### 界面说明

- **当前用户显示**：导航栏按钮显示当前用户 ID（最多显示 100 字符）
- **用户选择弹窗**：
  - 显示当前用户（带绿色勾选标记）
  - 输入框用于输入新用户 ID
  - 快速选择按钮显示常用用户和最近使用的用户

## 兼容性

### 向后兼容

- 如果 `localStorage` 中没有用户 ID，会使用环境变量 `NEXT_PUBLIC_USER_ID` 或默认值 `"user"`
- 环境变量仍然可以作为默认值使用

### 数据隔离

- 不同用户 ID 的记忆数据完全隔离
- 切换用户后，需要重新加载记忆数据

## 常见问题

### Q: 切换用户后，为什么看不到之前的记忆？

A: 不同用户 ID 的记忆数据是隔离的。切换用户后，需要重新加载该用户的记忆数据。

### Q: 用户选择会保存多久？

A: 用户选择保存在浏览器的 `localStorage` 中，除非清除浏览器数据，否则会一直保存。

### Q: 可以同时使用多个用户吗？

A: 不可以。一次只能选择一个用户。如果需要查看其他用户的记忆，需要切换用户。

### Q: 环境变量 `NEXT_PUBLIC_USER_ID` 还有用吗？

A: 有用。它作为默认值使用。如果 `localStorage` 中没有保存的用户 ID，会使用环境变量。

## 参考

- [Redux Store](../projects/mem0/openmemory/ui/store/profileSlice.ts)
- [UserSelector 组件](../projects/mem0/openmemory/ui/components/UserSelector.tsx)
- [Navbar 组件](../projects/mem0/openmemory/ui/components/Navbar.tsx)

