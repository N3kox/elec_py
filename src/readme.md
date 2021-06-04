### 1. 运行环境
- Neo 4j : https://neo4j.com/download-center/
- Python 3.7
### 2. 部署
### 2.1 Neo 4j
- 含GUI（Neo 4j Desktop），按程序指导进行启动即可。
- 无GUI，进入Neo 4j目录
```
cd neo4j/bin
./neo4j start
```
- 启动成功终端显示：
```
Starting Neo4j.Started neo4j (pid 30914). It is available at http://localhost:7474/ There may be a short delay until the server is ready.
```
（1）访问页面：http://localhost:7474

（2）初始账户和密码均为`neo4j`（`host`类型选择`bolt`）

（3）输入旧密码、输入新密码：启动前注意本地已安装`jdk`（建议安装`jdk`版本11）：https://www.oracle.com/java/technologies/javase-downloads.html

### 2.2 Python
- 解压源码后：
```
# 开启虚拟环境
conda activate your_virtual_env

# 安装pip
conda install pip

# 切换至源码目录中
cd webSprider/src

# 安装运行环境
pip install -r requirements.txt
```
- 构建数据目录，格式如下。其中运检数据文件放在data目录中，停用词放入stopwords文件夹中
```
.
├── data
│   ├── csvlog
│   ├── json
│   ├── logs
│   ├── pickles
│   └── stopwords
├── 工单.csv
├── 工作票.csv
├── 修饰记录.csv
├── 设备台账.csv
└── 标准工作任务单.csv
```
- 配置static.py:
```
dir = 'data上级目录绝对地址'
stopFileDir = '停用词表文件地址'
addr = (neo4j运行ip地址, bolt端口)
auth = (neo4j账号, neo4j密码)
```

### 3.运行
### 3.1 图谱构建
- 运行`preprocess.py`，此脚本会基于data目录中的csv数据自动构建电力运检知识图谱。
- 运行前请确认Neo 4j启动且库中内容为空，否则会出现数据混乱。
### 3.2 工单处理链路
- 运行`mission_linker.py`，json目录下获得`mission_links.json`，`mission_links_start.json`,`mission_links_end.json`文件
- 工单处理方案链路可以为后续运检方案查询提供支持
### 3.3 术语知识
- 运行`ws4mission.py`,基于运检非结构化文本进行分词、词性标注、术语知识爬取，获得`entity_index.json`作为术语知识的集合
- 运行`entity_keywords.py`,进行术语关键词抽取，建立倒排索引，获得`entity_keywords.json`和`entity_keywords_reverse.json`

### License
MIT License