# WebSphere Application Server 8.5.5.22 ICMRM 加密配置指南

## 📋 概述

IBM WebSphere Application Server 8.5.5.22 默认使用 XOR 加密方式存储密码（格式：`{xor}...`），这种加密方式安全性较低，容易被破解。本文档介绍如何使用 IBM ICMRM（IBM Content Manager Resource Manager）自定义密码加密来替换默认的 XOR 加密，提高系统安全性。

## ⚠️ 问题说明

### XOR 加密的安全风险

在 `security.xml` 文件中，密钥库密码使用 XOR 加密存储：

```xml
<keystores ... password="{xor}CD09Hgw=" ... />
<keySets ... password="{xor}CD09Hqw=" ... />
```

**XOR 加密的问题：**
- 加密算法简单，容易被破解
- 仅提供基本的混淆，不提供真正的安全保护
- 存在多个已知的安全漏洞（CVE-2022-43917 等）

### 解决方案

使用 IBM ICMRM 自定义密码加密，将密码格式从 `{xor}...` 升级为 `{custom:icmrm}...`，提供更强的加密保护。

## 🔧 配置步骤

### 前置条件

1. **确认 WebSphere 版本**
   ```bash
   cd /was8.5/websphere/AppServer/bin
   ./versionInfo.sh
   ```
   确保版本为 8.5.5.22 或更高。

2. **确认 IBM Content Manager 安装**
   - 需要安装 IBM Content Manager
   - 确认 `IBMCMROOT` 环境变量已设置
   - 确认 `IBMCMROOT/bin/generateWASKey` 脚本存在

3. **备份配置文件**
   ```bash
   # 备份 security.xml
   cp /was8.5/websphere/AppServer/profiles/Dmgr01/config/cells/c5-yy4ayj-web1ce1102/security.xml \
      /was8.5/websphere/AppServer/profiles/Dmgr01/config/cells/c5-yy4ayj-web1ce1102/security.xml.bak
   
   # 备份整个配置目录（推荐）
   tar -czf was_config_backup_$(date +%Y%m%d).tar.gz \
       /was8.5/websphere/AppServer/profiles/Dmgr01/config/
   ```

### 步骤 1：生成加密密钥文件

#### 1.1 进入 IBM Content Manager 目录

```bash
cd $IBMCMROOT/bin
# 或直接使用完整路径
cd /opt/IBM/ContentManager/bin
```

#### 1.2 生成密钥文件

**方式 A：使用密码短语生成（推荐，便于跨环境一致性）**

```bash
./generateWASKey -passphrase "your_secure_passphrase_at_least_32_characters_long"
```

**方式 B：随机生成（每次生成不同）**

```bash
./generateWASKey -nopassphrase
```

**参数说明：**
- `-passphrase`: 使用指定的密码短语生成密钥，确保在不同环境中使用相同密钥
- `-nopassphrase`: 随机生成密钥
- **重要**：密码短语必须至少 32 个字符

**输出：**
- 生成 `icmrm.sk` 文件
- 如果文件已存在，会自动重命名为 `icmrm.sk.bak`

#### 1.3 验证密钥文件

```bash
ls -lh icmrm.sk
# 应该看到 icmrm.sk 文件，大小通常为几 KB
```

### 步骤 2：部署密钥文件

#### 2.1 创建密钥文件目录

```bash
# 在 WebSphere 配置目录下创建密钥目录
mkdir -p /was8.5/websphere/AppServer/profiles/Dmgr01/properties/security
```

#### 2.2 复制密钥文件

```bash
# 复制密钥文件到安全目录
cp $IBMCMROOT/bin/icmrm.sk \
   /was8.5/websphere/AppServer/profiles/Dmgr01/properties/security/icmrm.sk

# 设置适当的权限（仅管理员可读写）
chmod 600 /was8.5/websphere/AppServer/profiles/Dmgr01/properties/security/icmrm.sk
chown wasadmin:wasgroup /was8.5/websphere/AppServer/profiles/Dmgr01/properties/security/icmrm.sk
```

#### 2.3 集群环境处理

如果是集群环境，需要在**所有节点**上执行相同操作：

```bash
# 在每个节点上创建目录并复制密钥文件
# Node 1
scp icmrm.sk node1:/was8.5/websphere/AppServer/profiles/Dmgr01/properties/security/

# Node 2
scp icmrm.sk node2:/was8.5/websphere/AppServer/profiles/Dmgr01/properties/security/

# ... 其他节点
```

**重要：** 所有节点必须使用**相同的** `icmrm.sk` 文件。

### 步骤 3：配置 WebSphere 使用自定义加密

#### 3.1 添加 JAR 文件到类路径

确认 `rmsecurity.jar` 文件存在：

```bash
ls -lh $IBMCMROOT/config/rmsecurity.jar
# 或
ls -lh /opt/IBM/ContentManager/config/rmsecurity.jar
```

**方法 A：通过管理控制台添加**

1. 登录 WebSphere 管理控制台
2. 进入：**服务器** → **服务器类型** → **WebSphere Application Server** → **[服务器名]**
3. 进入：**Java 和进程管理** → **进程定义** → **Java 虚拟机**
4. 在"类路径"中添加：
   ```
   $IBMCMROOT/config/rmsecurity.jar
   ```
   或完整路径：
   ```
   /opt/IBM/ContentManager/config/rmsecurity.jar
   ```

**方法 B：直接修改 server.xml（高级用户）**

在 `server.xml` 的 `<classpath>` 元素中添加：
```xml
<classpath>${IBMCMROOT}/config/rmsecurity.jar</classpath>
```

#### 3.2 配置 JVM 系统属性

**通过管理控制台配置：**

1. 登录 WebSphere 管理控制台
2. 进入：**服务器** → **服务器类型** → **WebSphere Application Server** → **[服务器名]**
3. 进入：**Java 和进程管理** → **进程定义** → **Java 虚拟机**
4. 在"通用 JVM 参数"中添加以下参数：

```
-Dcom.ibm.wsspi.security.crypto.customPasswordEncryptionClass=com.ibm.cm.postinstall.icmrm.security.RMWASEncryption
-Dcom.ibm.wsspi.security.crypto.customPasswordEncryptionEnabled=true
-Dcom.ibm.icmrm.security.keyfolder=/was8.5/websphere/AppServer/profiles/Dmgr01/properties/security
```

**参数说明：**
- `customPasswordEncryptionClass`: 自定义加密类的完全限定名
- `customPasswordEncryptionEnabled`: 启用自定义密码加密
- `com.ibm.icmrm.security.keyfolder`: `icmrm.sk` 文件所在的目录路径

**集群环境：**
- 需要在**每个服务器节点**上配置相同的 JVM 参数
- 确保每个节点的 `keyfolder` 路径指向正确的密钥文件位置

### 步骤 4：重启 WebSphere 服务

#### 4.1 停止服务

```bash
# 停止 Deployment Manager
/was8.5/websphere/AppServer/profiles/Dmgr01/bin/stopManager.sh

# 停止节点代理（如果有）
/was8.5/websphere/AppServer/profiles/AppSrv01/bin/stopNode.sh

# 停止应用服务器
/was8.5/websphere/AppServer/profiles/AppSrv01/bin/stopServer.sh server1
```

#### 4.2 启动服务

```bash
# 启动 Deployment Manager
/was8.5/websphere/AppServer/profiles/Dmgr01/bin/startManager.sh

# 启动节点代理
/was8.5/websphere/AppServer/profiles/AppSrv01/bin/startNode.sh

# 启动应用服务器
/was8.5/websphere/AppServer/profiles/AppSrv01/bin/startServer.sh server1
```

#### 4.3 验证启动

检查日志文件，确认没有加密相关的错误：

```bash
tail -f /was8.5/websphere/AppServer/profiles/Dmgr01/logs/dmgr/SystemOut.log
```

### 步骤 5：更新现有密码

重启后，需要重新设置所有密钥库密码，使其使用新的加密方式。

#### 5.1 通过管理控制台更新密码

1. 登录 WebSphere 管理控制台
2. 进入：**安全性** → **SSL 证书和密钥管理** → **密钥库和证书**
3. 逐个编辑每个密钥库：
   - 点击密钥库名称
   - 点击"编辑"
   - 重新输入密码（或保持原密码）
   - 点击"确定"保存

4. 对于密钥集（Key Sets）：
   - 进入：**安全性** → **SSL 证书和密钥管理** → **密钥集**
   - 编辑每个密钥集，重新输入密码

#### 5.2 验证密码加密格式

更新密码后，检查 `security.xml` 文件：

```bash
grep -i "password=" /was8.5/websphere/AppServer/profiles/Dmgr01/config/cells/*/security.xml
```

**应该看到：**
```xml
password="{custom:icmrm}Lz4sLB8oMC07bm0="
```

**不应该再看到：**
```xml
password="{xor}CD09Hgw="
```

## ✅ 验证配置

### 检查脚本

创建验证脚本 `verify_encryption.sh`：

```bash
#!/bin/bash

SECURITY_XML="/was8.5/websphere/AppServer/profiles/Dmgr01/config/cells/c5-yy4ayj-web1ce1102/security.xml"

echo "=========================================="
echo "WebSphere 密码加密配置验证"
echo "=========================================="
echo ""

# 检查 XOR 加密（不安全）
echo "1. 检查 XOR 加密密码（不安全）："
xor_count=$(grep -o '{xor}' "$SECURITY_XML" 2>/dev/null | wc -l | tr -d ' ')
if [ "$xor_count" -gt 0 ]; then
    echo "   ⚠️  发现 $xor_count 个使用 XOR 加密的密码"
    echo "   建议立即更新这些密码"
    grep -n '{xor}' "$SECURITY_XML" 2>/dev/null | head -5
else
    echo "   ✅ 未发现 XOR 加密密码"
fi

echo ""

# 检查自定义加密（安全）
echo "2. 检查 ICMRM 自定义加密密码（安全）："
custom_count=$(grep -o '{custom:icmrm}' "$SECURITY_XML" 2>/dev/null | wc -l | tr -d ' ')
if [ "$custom_count" -gt 0 ]; then
    echo "   ✅ 发现 $custom_count 个使用 ICMRM 加密的密码"
    grep -n '{custom:icmrm}' "$SECURITY_XML" 2>/dev/null | head -5
else
    echo "   ⚠️  未发现 ICMRM 加密密码"
    echo "   请确认配置是否正确"
fi

echo ""

# 检查密钥文件
echo "3. 检查密钥文件："
KEY_FILE="/was8.5/websphere/AppServer/profiles/Dmgr01/properties/security/icmrm.sk"
if [ -f "$KEY_FILE" ]; then
    echo "   ✅ 密钥文件存在: $KEY_FILE"
    ls -lh "$KEY_FILE"
else
    echo "   ⚠️  密钥文件不存在: $KEY_FILE"
fi

echo ""

# 检查 JVM 参数
echo "4. 检查 JVM 配置："
echo "   请手动检查管理控制台中的 JVM 参数是否包含："
echo "   - com.ibm.wsspi.security.crypto.customPasswordEncryptionClass"
echo "   - com.ibm.wsspi.security.crypto.customPasswordEncryptionEnabled"
echo "   - com.ibm.icmrm.security.keyfolder"

echo ""
echo "=========================================="
```

运行验证脚本：

```bash
chmod +x verify_encryption.sh
./verify_encryption.sh
```

## 🔄 回滚操作

如果需要回滚到 XOR 加密（不推荐）：

### 步骤 1：禁用自定义加密

在 JVM 参数中设置：
```
-Dcom.ibm.wsspi.security.crypto.customPasswordEncryptionEnabled=false
```

### 步骤 2：重启服务

重启所有 WebSphere 服务。

### 步骤 3：更新密码

在管理控制台中重新设置所有密码，系统会自动使用 XOR 加密。

## 📚 参考文档

### IBM 官方文档

1. **IBM Content Manager - 使用 WebSphere Application Server 自定义密码加密加密数据库凭据**
   - 链接：https://www.ibm.com/docs/ro/SSRS7Z_8.5.0/com.ibm.installingcm.doc/dcmcw353.htm
   - 这是最详细的官方配置文档

2. **WebSphere Application Server 8.5 信息中心**
   - 搜索关键词：`custom password encryption`
   - 链接：https://www.ibm.com/docs/en/was-nd/8.5.5

3. **故障排查 - ICM9839 加密错误**
   - 链接：https://www.ibm.com/support/pages/starting-resource-manager-gives-error-icm9839-encryption-error-null-log-files-ibm-websphere-application-server-version-6-or-after-applying-latest-java-development-kit-updates-ibm-websphere-application-server-version-511

### 相关安全漏洞

- **CVE-2022-43917**: 加密强度不足漏洞
- **CVE-2025-33142**: 证书验证不当漏洞
- **CVE-2025-36038**: 反序列化远程代码执行漏洞（严重）

## ⚠️ 重要注意事项

### 安全建议

1. **密钥文件保护**
   - 密钥文件 `icmrm.sk` 必须妥善保管
   - 设置严格的文件权限（600）
   - 不要将密钥文件提交到版本控制系统
   - 定期备份密钥文件到安全位置

2. **密码短语管理**
   - 使用强密码短语（至少 32 个字符）
   - 记录密码短语到安全的密码管理系统
   - 不要将密码短语写在配置文件中

3. **定期更换密钥**
   - 建议每 6-12 个月更换一次密钥文件
   - 更换密钥时，需要重新设置所有密码

4. **集群环境**
   - 所有节点必须使用相同的密钥文件
   - 确保密钥文件同步到所有节点
   - 使用配置管理工具（如 Ansible）自动化部署

5. **备份策略**
   - 配置更改前必须备份
   - 备份 `security.xml` 和整个配置目录
   - 备份密钥文件到安全位置

### 常见问题

**Q1: 配置后密码仍然是 `{xor}` 格式？**

A: 可能的原因：
- JVM 参数未正确配置
- `rmsecurity.jar` 未添加到类路径
- 密钥文件路径不正确
- 服务未重启

解决：检查配置并重启服务，然后重新设置密码。

**Q2: 启动时出现加密错误？**

A: 检查：
- 密钥文件是否存在且可读
- 密钥文件路径是否正确
- 文件权限是否正确
- 查看日志文件获取详细错误信息

**Q3: 集群环境中部分节点加密失败？**

A: 确保：
- 所有节点使用相同的密钥文件
- 所有节点的 JVM 参数配置一致
- 密钥文件已同步到所有节点

## 📝 配置检查清单

配置完成后，请确认：

- [ ] 已备份 `security.xml` 和配置目录
- [ ] 已生成 `icmrm.sk` 密钥文件
- [ ] 密钥文件已部署到所有节点
- [ ] 密钥文件权限设置为 600
- [ ] `rmsecurity.jar` 已添加到类路径
- [ ] JVM 参数已正确配置
- [ ] 所有服务已重启
- [ ] 所有密钥库密码已更新
- [ ] `security.xml` 中的密码格式为 `{custom:icmrm}...`
- [ ] 验证脚本运行正常
- [ ] 应用功能正常

## 🔗 相关文档

- [WebSphere Application Server 安全配置最佳实践](./README.md)
- [WebSphere 部署指南](./README.md)

---

**文档版本**: 1.0  
**最后更新**: 2024-12-17  
**适用版本**: IBM WebSphere Application Server 8.5.5.22+
