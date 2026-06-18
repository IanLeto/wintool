# K8s 集群管理功能说明

## 📋 功能概述

K8s 集群管理工具允许你在内网环境中管理多个 Kubernetes 集群，并批量执行 kubectl 命令。

## ✨ 主要功能

### 1. 集群列表展示
- 📊 显示所有可用的 K8s 集群
- ✅ 标识当前活动的集群
- 📝 显示集群的命名空间和用户信息
- 🔄 支持刷新集群列表

### 2. 批量命令执行
- ⚡ 在多个集群上同时执行 kubectl 命令
- 📦 预置常用命令模板（查看 Pods、节点、服务等）
- ⏱️ 显示每个命令的执行时间
- 📊 统计成功/失败数量

### 3. 执行结果展示
- ✅ 清晰区分成功和失败的结果
- 📋 支持复制命令输出
- 🎨 语法高亮的输出显示
- 📈 实时显示执行进度

## 🚀 使用方法

### 配置 kubeconfig 文件

#### 方式1：使用示例文件（推荐）
```bash
# 1. 复制示例文件
cp kubeconfig.example kubeconfig

# 2. 编辑 kubeconfig 文件，填入你的集群信息
vim kubeconfig
```

#### 方式2：使用现有配置
```bash
# 从默认位置复制
cp ~/.kube/config kubeconfig

# 或者创建软链接
ln -s ~/.kube/config kubeconfig
```

### 启动应用

```bash
# 启动服务
./start.sh

# 访问应用
open http://localhost:8080
```

### 使用界面

1. **选择集群**
   - 点击集群卡片或勾选复选框
   - 支持全选/取消全选
   - 当前活动集群会有绿色标识

2. **执行命令**
   - 选择预置命令模板，或
   - 手动输入 kubectl 命令（不需要 kubectl 前缀）
   - 点击"执行命令"按钮

3. **查看结果**
   - 成功的结果显示为绿色边框
   - 失败的结果显示为红色边框
   - 点击"复制"按钮复制输出内容

## 📝 命令示例

### 预置命令模板

| 模板名称 | 命令 | 说明 |
|---------|------|------|
| 查看 Pods | `get pods -A` | 查看所有命名空间的 Pods |
| 查看节点 | `get nodes` | 查看集群节点状态 |
| 查看服务 | `get svc -A` | 查看所有服务 |
| 查看部署 | `get deployments -A` | 查看所有部署 |
| 查看命名空间 | `get namespaces` | 查看所有命名空间 |
| 集群信息 | `cluster-info` | 查看集群信息 |
| 查看事件 | `get events -A --sort-by=.metadata.creationTimestamp` | 查看最近事件 |

### 自定义命令示例

```bash
# 查看特定命名空间的 Pods
get pods -n production

# 查看 Pod 详情
describe pod <pod-name> -n <namespace>

# 查看 Pod 日志
logs <pod-name> -n <namespace>

# 查看资源使用情况
top nodes
top pods -A

# 应用配置
apply -f deployment.yaml

# 删除资源
delete pod <pod-name> -n <namespace>
```

## 🔧 技术实现

### 后端 API

#### 1. 获取集群列表
```
GET /api/k8s/clusters
```

返回所有配置的集群信息。

#### 2. 批量执行命令
```
POST /api/k8s/execute
Content-Type: application/json

{
  "clusters": ["cluster-1", "cluster-2"],
  "command": "get pods -A"
}
```

在指定集群上执行命令，返回每个集群的执行结果。

#### 3. 切换上下文
```
POST /api/k8s/switch-context
Content-Type: application/json

{
  "context": "cluster-1"
}
```

切换当前活动的集群上下文。

### 前端组件

- **K8sClusterTool.vue** - 主组件
- 使用 Vue 3 Composition API
- 响应式设计，支持移动端
- 实时状态更新

### 配置文件

- **kubeconfig** - K8s 配置文件（与启动脚本同目录）
- 支持标准的 kubeconfig 格式
- 可配置多个集群、用户和上下文

## 🛡️ 安全说明

### 权限控制

- 命令执行使用配置文件中的用户权限
- 建议使用只读权限的用户进行查询操作
- 危险操作（delete、apply 等）需谨慎使用

### 配置文件安全

```bash
# 设置 kubeconfig 文件权限
chmod 600 kubeconfig

# 不要将 kubeconfig 提交到版本控制
echo "kubeconfig" >> .gitignore
```

### 网络安全

- 应用默认监听 0.0.0.0:8080
- 建议在内网环境使用
- 可配置防火墙规则限制访问

## 📊 故障排除

### 问题1: 无法获取集群列表

**可能原因:**
- kubeconfig 文件不存在或格式错误
- kubectl 命令未安装
- 集群连接失败

**解决方法:**
```bash
# 检查 kubeconfig 文件
cat kubeconfig

# 测试 kubectl 命令
kubectl --kubeconfig=kubeconfig get nodes

# 检查集群连接
kubectl --kubeconfig=kubeconfig cluster-info
```

### 问题2: 命令执行超时

**可能原因:**
- 集群响应慢
- 网络延迟高
- 命令执行时间过长

**解决方法:**
- 后端默认超时时间为 30 秒
- 可修改 `backend-python/app.py` 中的 `timeout` 参数
- 使用更具体的命令减少输出

### 问题3: 权限不足

**可能原因:**
- kubeconfig 中的用户权限不足
- RBAC 配置限制

**解决方法:**
```bash
# 检查当前用户权限
kubectl --kubeconfig=kubeconfig auth can-i --list

# 使用有足够权限的用户
# 编辑 kubeconfig 文件更换用户
```

## 🎯 最佳实践

### 1. 命名规范

- 使用有意义的集群名称
- 统一命名空间命名规则
- 标签化管理资源

### 2. 批量操作

- 先在单个集群测试命令
- 确认无误后再批量执行
- 重要操作前备份配置

### 3. 监控和日志

```bash
# 定期检查集群状态
get nodes
get pods -A

# 查看最近事件
get events -A --sort-by=.metadata.creationTimestamp | tail -20

# 监控资源使用
top nodes
top pods -A
```

### 4. 安全操作

- 使用只读用户进行查询
- 危险操作需要二次确认
- 定期审计操作日志
- 限制网络访问范围

## 📚 参考资料

- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [kubectl 命令参考](https://kubernetes.io/docs/reference/kubectl/)
- [kubeconfig 配置说明](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/)

## 🔄 更新日志

### v1.0.0 (2026-06-17)
- ✅ 初始版本发布
- ✅ 支持多集群管理
- ✅ 批量命令执行
- ✅ 预置命令模板
- ✅ 执行结果展示
- ✅ 完全离线部署

## 💡 未来计划

- [ ] 支持命令历史记录
- [ ] 添加更多预置命令模板
- [ ] 支持命令收藏功能
- [ ] 添加集群健康检查
- [ ] 支持 YAML 文件编辑和应用
- [ ] 添加资源可视化图表
- [ ] 支持多用户权限管理

## 📞 技术支持

如有问题或建议，请联系开发团队。
