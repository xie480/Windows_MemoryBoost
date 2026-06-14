# MemGuardian

高性能 Windows 内存优化工具，支持自动后台监控与内存优化。

---

## 效果

可将系统内存占用率从：

```text
90%+ → 30%
```

同时保持正常使用体验，不影响日常办公、开发及游戏。

> 实际效果受 CPU、内存容量、后台程序数量等因素影响。

---

# 使用教程

## 1. 配置 Windows 任务计划程序

首先需要将：

```text
memory_boost.exe
```

加入 Windows 任务计划程序。

打开：

```text
Win + R
```

输入：

```text
taskschd.msc
```

点击：

```text
创建任务
```

### 常规

名称填写：

```text
MemoryBoost
```

勾选：

```text
☑ 使用最高权限运行
```

配置：

```text
Windows 10 / Windows 11
```

---

### 操作

程序填写：

```text
D:\Windows_MemoryBoost\memory_boost.exe
```

请修改为实际路径。

---

## 2. 测试任务是否成功

打开终端执行：

```bash
schtasks /run /tn "\MemoryBoost"
```

若内存占用明显下降，则说明配置成功。

---

## 3. 启动后台守护进程

编辑：

```text
memory_guardian.py
```

根据需要修改以下字段：

```python
DEFAULT_THRESHOLD = 90.0      # 触发阈值
DEFAULT_RELEASE = 80.0        # 恢复阈值
DEFAULT_INTERVAL = 5          # 检测间隔（秒）
DEFAULT_COOLDOWN = 120        # 冷却时间（秒）
```

推荐配置：

```text
触发阈值：90%
恢复阈值：80%
检测间隔：5 秒
冷却时间：120 秒
```

随后启动后台守护进程：

```bash
pythonw memory_guardian.py
```

启动后将自动后台运行，不会弹出控制台窗口。

---

## 工作流程

```text
检测内存占用
        ↓
超过阈值
        ↓
自动执行：

schtasks /run /tn "\MemoryBoost"

        ↓
触发内存优化
        ↓
进入冷却时间
        ↓
等待下一次触发
```

---

## 日志

后台日志默认保存为：

```text
memory_guardian.log
```

可用于查看：

- 触发记录
- 错误信息
- 运行状态

---

## License

MIT License
