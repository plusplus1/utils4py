# utils4py
---
My utilities for python

## 调试环境支持
> - 环境变量IS_DEBUG=1表示调试模式，其他表示生产环境；

## 配置支持
> - 默认支持python ConfigParser解析，参考 utils4py.ConfUtils
> - 调试环境下，默认读取 conf_test 目录下配置；
> - 生产环境下，默认读取 conf 目录下配置；


## 附: 工具列表
| 模块        | 功能说明    |
| :--------: | :-------- |
| utils4py.env | 识别是否是调试环境，is_debug 函数 |
| utils4py.ConfUtils | 配置加载工具 |
| utils4py.TextUtils | 字符相关工具，to_string, json_loads, json_dumps | 
| utils4py.ErrUtils | 错误信息处理 |
| utils4py.ArgsChecker | 参数检查 |
| utils4py.scan | 包扫描 |

