-- 创建数据表
CREATE TABLE `weibo_user_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `wuid` varchar(50) DEFAULT NULL,
  `nickname` varchar(21) DEFAULT NULL,
  `portrait_url` varchar(100) DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `birthday` varchar(20) DEFAULT NULL,
  `weibo_num` int(11) DEFAULT NULL,
  `fans_num` int(11) DEFAULT NULL,
  `follow_num` int(11) DEFAULT NULL,
  `verified` int(11) DEFAULT NULL,
  `vip` int(11) DEFAULT NULL,
  `relationship_state` varchar(10) DEFAULT NULL,
  `address` varchar(50) DEFAULT NULL,
  `tags` varchar(100) DEFAULT NULL,
  `original_blog_num` int(11) DEFAULT NULL,
  `forward_blog_num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=637 DEFAULT CHARSET=utf8mb4

  SELECT count(*) FROM weibo_spider.weibo_user_info;

-- 查找重复数据
SELECT * FROM weibo_user_info
	WHERE wuid = ANY (
		SELECT wuid FROM weibo_user_info
		GROUP BY wuid HAVING COUNT(wuid) > 1);

-- 数据去重，保存在临时数据库中
SET SQL_SAFE_UPDATES=0;
drop table if exists tmp_usr;

create table tmp_usr as
	select id from weibo_user_info
		where id in (
			select max(id) from weibo_user_info
			group by wuid);

-- 删除重复数据
delete from weibo_spider.weibo_user_info
	where id not in  (
		select id from tmp_usr);

-- 删除临时数据库
drop table if exists tmp_usr ;