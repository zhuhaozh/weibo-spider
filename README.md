# 微博爬虫 V0.699

### 简介
基于python 3.5.2 开发的微博爬虫程序。


### 更新详情
1. 添加了微博的登陆功能
2. 添加了 CookiesPool ，防止403，自动管理多个账号的登陆问题
3. 数据库添加了uni_code column，方便后期数据库数据去重 
4. 修复bugs若干

### 主要功能

1. 自动爬取微博博主的7条最新粉丝记录以及10条微博记录
2. 可自动分辨转发微博与原创微博被分别存储到不同的数据库表中
3. 自动将所有的粉丝id记录存储在集合中，作为待使用记录
4. 可设置自动备份，包括内存备份与磁盘文件备份，同时可自动恢复记录信息
5. 使用CookiesPool连接池，自动管理微博信息，有效防止403

### 数据库

* 使用pymysql连接mysql数据库，表信息sqls文件夹中，可直接导入
* 需要在db.conf配置文件中配置数据库信息，并确保编码格式为utf8mb4
 
```shell 
   安装 pymysql :
   sudo pip3 install pymysql   
```

### 使用方法
  * 直接调用WeiboSpiderClient(init_id)，传入参数为博主的id信息，注意：不是昵称！eg:1195054531（博物杂志）
  * 可通过链式调用设置参数，如是否备份到文件等信息。
  注意：如果未调用setBackupToFile(trueOrFalse)，则不使用备份。建议使用。


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
* 需要手动输入验证码


#### 有关数据库方面：
* 由于emoji表情的存在，需要将数据库的编码更改为utf8mb4。否则会有部分信息存储时失败。
* 具体更改方法参考：http://www.linuxdiyf.com/linux/20851.html


### 其他 
* 由于比较懒，注释还不够详细，在今后会慢慢补上注释
* 由于对网页的分析不够充分，有许多部分在解析的过程中可能会出现错误所以造成爬出来的信息格式问题以及其他系列问题
* 备份采用at-least-once 语义，需要后期对数据去重。
* 今后打算把这个程序改成多线程版本
* 由于这是从Java转来的第一个Python小程序,Python也正处于边学边用的状态,故代码风格何java类似
* 现将部分该项目中，复用性很高的代码抽取出来放在了<a href="https://github.com/zzhy1996/zhlib">zhlib</a>这个项目中，欢迎查看