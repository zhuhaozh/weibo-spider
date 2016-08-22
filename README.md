# 微博爬虫 V0.9 

### 简介
基于python 3.5.2 开发的微博爬虫程序。

### 主要功能

1. 自动爬取微博博主的7条最新粉丝记录以及10条微博记录
2. 可自动分辨转发微博与原创微博被分别存储到不同的数据库表中
3. 自动将所有的粉丝id记录存储在集合中，作为待使用记录
4. 可设置自动备份，包括内存备份与磁盘文件备份，同时可自动恢复记录信息

### 数据库

* 使用pymysql连接mysql数据库，表信息sqls文件夹中，可直接导入
* 需要在db.conf配置文件中配置数据库信息，并确保编码格式为utf8
 
```shell 
   安装 pymysql :
   sudo pip3 install pymysql   
```

### 使用方法
  * 直接调用WeiboSpiderClient(init_id)，传入参数为博主的id信息，注意：不是昵称！eg:1195054531（博物杂志）
  * 可通过链式调用设置参数，如是否备份到文件等信息。
  注意：如果未调用setBackupToFile(trueOrFalse)，则不使用备份！


```python
    initId = '1195054531'
  
    WeiboSpiderClient(initId) \
        .setBackupToFile(True) \
        .setSleepSeconds(2) \
        .setLimitRecords(1000) \
        .setRecoverTimes(3) \
        .run()
```

### 注意事项

#### 有关微博登陆方面：

* 该程序暂时采用手动携带cookies来登陆，需要在 **weibo_url_headers.conf** 配置文件中配置响应头。
* 配置文件中包含但不限于 Cookie , User-Agent 等
* cookies的获取：用自己的微博账号登陆手机版微博网页：weibo.cn，使用chrome开发者工具或其他工具获取到响应头的cookie属性，复制到配置文件中
*  exmaple :
``` conf 
 Cookie:cookies-examples.etc
 User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36
```

#### 有关数据库方面：
* 由于emoji表情的存在，需要将数据库的编码更改为utf8mb4。否则会有部分信息存储时失败。
* 具体更改方法参考：http://www.linuxdiyf.com/linux/20851.html


### 其他 
* 由于比较懒，注释还不够详细，在今后会慢慢补上注释
* 由于对网页的分析不够充分，有许多部分在解析的过程中可能会出现错误所以造成爬出来的信息格式问题以及其他系列问题
* 今后打算把这个程序改成多线程版本
