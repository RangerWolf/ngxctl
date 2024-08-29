# 背景
参考ngxtop项目，对其进行改造，并尝试结合其他nginx的一些开源项目，增强or恢复功能

# 支持的功能
## 1) nginx top
已经支持，还有一些小问题  

```bash
-- 默认命令， 直接读取/etc/nginx/nginx.conf
ngxctl top  


```


# 本地调试
1. install.sh  
   直接本地安装，系统能直接`ngxctl top` 运行

2. 不install，而是直接运行  
   ```bash
   -- 启动虚拟环境
   conda activate ngxtools  
   -- 直接运行
   cd ngxctl
   python cli.py
   python cli.py top
   python cli.py top --no-follow
   
   ```
