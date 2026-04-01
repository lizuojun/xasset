说明：智能布局算法，支持单屋和全屋软装方案生成，包括布局算法，微调算法，组合算法等
模式：包括迁移布局、推荐布局、方案布局、调整布局四种布局模式

*   主要模块：
   - ImportHouse 导入空户型，负责解析空户型，提取近似的样板间及功能区
   - LayoutByRule 规则化布局模块，负责全屋的布局方案生成，每个房间根据样板生成典型布局方案，包括家具位置、朝向
   - LayoutEvaluation 布局评价模块，负责功能区布局的评价，暂时无用
*   支撑模块：
   - House 户型解析模块，执行户型json数据的解析和特征提取
   - Furniture 家具解析模块，执行家具模型数据的解析和特征提取
*   测试模块：
    - LayoutTest 算法测试模块
*   依赖模块：
   - oss2 requests flask waitress (数据下载及服务访问)
   - numpy (数值计算)
   - matplotlib (绘制显示)
   - scipy shapely (户型解析)
   - trimesh (户型重建)
   - threadpool (硬装铺贴)
*   依赖模块：
   - pyopengl pygame pillow (模型解析 布局算法不需安装)
*   依赖模块：
   - pyopengl pygame (前端演示 布局算法不需安装)
   - tqdm (进度演示 布局算法不需安装)
*   依赖模块：
   - alibaba-sdk-secretsmanager-common-plugin
   - aliyun-sdk-secretsmanager-sdk-core-plugin
   - aliyun-sdk-secretsmanager-oss-plugin
   - aliyun-sdk-secretsmanager-sls-plugin


*   服务入口：
    - layout_propose 推荐布局服务入口 设计家的智能设计链路，包括智能软装、一键迁移、定制设计等
    - layout_sample 方案布局服务入口 躺平家的布局算法链路，包括我的家、放我家等
    - layout_group 组合布局服务入口 设计家的智能设计链路，包括一键配饰、组合提取、组合生成等
