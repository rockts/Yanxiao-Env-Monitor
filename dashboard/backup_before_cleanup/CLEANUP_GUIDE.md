# 智慧校园环境监测系统 - 重构完成指南

## 文件重组已基本完成

项目已按新的目录结构进行了重组，但根目录下仍有许多遗留文件。为了完全整理项目，请按照以下步骤操作：

### 1. 运行整理脚本清理文件

```bash
# 在项目根目录下运行
./organize_files.sh
```

此脚本会：
- 将所有.command脚本移动到scripts/unix目录
- 将所有.bat脚本移动到scripts/windows目录
- 将所有.sh脚本移动到scripts/unix目录
- 将备份的Python文件移动到backup目录
- 确保配置文件在config目录
- 将旧文件临时存放在old_files目录中

### 2. 检查新的启动方式

新的项目提供了多种启动方式：

```bash
# 方法1: 使用统一启动器
./launch.py [选项]

# 方法2: 使用整理后的脚本
./scripts/unix/start_dashboard.command

# 方法3: 直接启动主程序
python3 src/main_dashboard.py
```

### 3. 测试新的项目结构

请测试以下功能是否正常工作：
- 基本仪表盘启动
- 与MQTT服务器的连接
- 数据显示和图表更新
- 视频流显示(如果适用)

### 4. 完成重构

确认一切功能正常后：
1. 可以删除根目录下的old_files目录(包含所有被移动的文件)
2. 确保scripts目录中的脚本都能正常工作
3. 更新任何可能依赖旧路径的外部引用

### 5. 更新文档

重构已经更新了项目文档，请查看以下文件了解详情：
- README.md: 更新的项目主文档
- REFACTOR_SUMMARY.md: 重构摘要和后续工作
- restructure_checklist.md: 重构检查清单

## 注意事项

- 所有旧的功能已保留，只是文件位置发生了变化
- 根目录下的main.py现在是一个导入转发层，仍兼容旧的导入方式
- 新的主入口是src/main_dashboard.py
- 配置文件仍然位于config目录，优先使用local_config.json
