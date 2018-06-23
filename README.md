# utils4py 
整理开发中经常用的一些python工具包，提高生产效率


## 1. 调试环境支持
> - 环境变量IS_DEBUG=1表示调试模式，其他表示生产环境；

## 2. 配置支持
> - 默认支持python ConfigParser解析，参考 utils4py.ConfUtils
> - 调试环境下，默认读取 conf_test 目录下配置；
> - 生产环境下，默认读取 conf 目录下配置；

## 3.数据源相关
### 3.1） mysql连接
> - 默认配置路径 conf(_test)/data_source/mysql.conf
> - 配置格式
>>```
>>[xxxxx]
>>host            =   localhost
>>port            =   3306
>>user            =   xxx
>>password        =   xxx
>>db              =   xxx
>>charset         =   utf8
>>time_zone       =   +8:00
>>```
> - 使用示例
>>```python
>>from utils4py.data import connect_mysql
>>db = connect_mysql("xxxxx")
>>```
> - 默认自动提交
> - 事务支持

### 3.2）redis连接
> - 默认配置路径 conf(_test)/data_source/redis.conf
> - 配置格式
>>```
>>[xxxxx]
>>host            =   localhost
>>port            =   3306
>>password        =   xxx
>>db              =   0
>>```
> - 使用示例
>>```python
>>from utils4py.data import connect_redis
>>r = connect_redis("xxxxx")
>>```
> - 在原redis连接基础上进行代理包装，常用操作自动在将key打上前缀 `xxxxx:`

---
## 4. 服务相关
### 4.1） flask服务
| 模块 | 功能说明 | 使用方法 |
| :---: | :--- | :--- |
| utils4py.flask_ext.server.AppServer | server默认实现 | 初始化filter_paths和route_paths, 服务启动后自动扫描并加载filter和路由 |
| utils4py.flask_ext.filter.BaseFilter | 所有filter基类 | 自定义filter继承此类，并实现before_request和after_request |
| utils4py.flask_ext.routes.BaseService | 所有flask路由具体执行者基类 | 继承此类，并实现抽象方法check_args和run |
| utils4py.flask_ext.routes.service_route | 路由装饰器 | 对路由具体执行者加上此装饰器，AppServer启动时会扫描route_paths下所有此装饰器注册的路由服务 |

---
## 5. 离线相关
### 5.1) 多进程消费者
> 主要模块

| 模块 | 功能说明 | 使用方法 |
| :---: | :--- | :--- |
| utils4py.consume.MultiConsumer | 消费进程基类 | 继承并实现 init_queue 方法，并装饰各阶段功能函数 |
| utils4py.consume.Controller | 控制器 | 实例化并调用start方法，支持安全退出 |

> 需要自定义的功能函数装饰器
```python
from utils4py.comsume import MultiConsumer
D = MultiConsumer.D
```

| 装饰器 | 功能 | 备注 |
| :---: | :--- | :--- |
| D.prepare | 准备函数，初始化model | 只能注册一个，如果不注册，则使用默认实现 | 
| D.after_pop | 从队列获取数据之后执行,一般可以准备现场,备份消息之类的,以便于处理失败后可以捞回 | 可以有多个或者没有，按照注册index顺序执行 |
| D.execute | 执行具体业务 | 可以有多个，按照index顺序执行 |
| D.success | 前面所有阶段没有异常视为成功，则执行对应函数 | 可以有多个，按照index顺序执行 |
| D.fail | 前面任何地方有异常则执行，可用于执行恢复消息后者通知报警 | 可以有多个，按照index顺序执行 |


---
## 附: 工具列表
| 模块        | 功能说明    |
| :--------: | :-------- |
| utils4py.env | 识别是否是调试环境，is_debug 函数 |
| utils4py.ConfUtils | 配置加载工具 |
| utils4py.TextUtils | 字符相关工具，to_string, json_loads, json_dumps | 
| utils4py.ErrUtils | 错误信息处理 |
| utils4py.ArgsChecker | 参数检查 |
| utils4py.scan | 包扫描 |

