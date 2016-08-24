DROP TABLE `weibo_spider`.`weibo_forward_blog`;
CREATE TABLE `weibo_original_blog` (
  `wobid` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` varchar(40) DEFAULT NULL,
  `like_num` int(11) DEFAULT NULL,
  `comment_num` int(11) DEFAULT NULL,
  `forward_num` int(11) DEFAULT NULL,
  `pic_num` int(11) DEFAULT NULL,
  `via` varchar(50) DEFAULT NULL,
  `owner_id` varchar(30) DEFAULT NULL,
  `content` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`wobid`)
) ENGINE=InnoDB AUTO_INCREMENT=2171 DEFAULT CHARSET=utf8mb4

  SELECT count(*) FROM weibo_spider.weibo_original_blog;

-- 查找重复数据
SELECT count(*) FROM weibo_spider.weibo_original_blog
	WHERE uni_code = ANY (
		SELECT uni_code FROM weibo_original_blog
		GROUP BY uni_code HAVING COUNT(uni_code) > 1);

-- 数据去重，保存在临时数据库中
SET SQL_SAFE_UPDATES=0;
drop table if exists tmp_ob;
create table tmp_ob as
	select wobid from weibo_spider.weibo_original_blog
		where wobid in (
			select max(wobid) from weibo_spider.weibo_original_blog
			group by uni_code);

select count(wobid) from weibo_spider.weibo_original_blog
		where wobid in (
			select max(wobid) from weibo_spider.weibo_original_blog
			group by uni_code);

-- 删除重复数据
delete from weibo_spider.weibo_original_blog
	where wobid not in  (
		select wobid from tmp_ob);

-- 删除临时数据库
drop table if exists tmp_ob ;