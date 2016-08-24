
CREATE TABLE `weibo_forward_blog` (
  `wfbid` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` varchar(40) DEFAULT NULL,
  `like_num` int(11) DEFAULT NULL,
  `comment_num` int(11) DEFAULT NULL,
  `forward_num` int(11) DEFAULT NULL,
  `pic_num` int(11) DEFAULT NULL,
  `original_like_num` int(11) DEFAULT NULL,
  `original_comment_num` int(11) DEFAULT NULL,
  `original_forward_num` int(11) DEFAULT NULL,
  `original_pic_num` int(11) DEFAULT NULL,
  `via` varchar(50) DEFAULT NULL,
  `original_owner_id` varchar(30) DEFAULT NULL,
  `original_content` varchar(500) DEFAULT NULL,
  `forward_owner_id` varchar(30) DEFAULT NULL,
  `forward_content` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`wfbid`)
) ENGINE=InnoDB AUTO_INCREMENT=2757 DEFAULT CHARSET=utf8mb4

select count(*) from weibo_spider.weibo_forward_blog ;
-- 查找重复数据
SELECT * FROM weibo_spider.weibo_forward_blog
	WHERE uni_code = ANY (
		SELECT uni_code FROM weibo_forward_blog
		GROUP BY uni_code HAVING COUNT(uni_code) > 1);

-- 数据去重，保存在临时数据库中
SET SQL_SAFE_UPDATES=0;
drop table if exists tmp_fb;
create table tmp_fb as
	select wfbid from weibo_spider.weibo_forward_blog
		where wfbid in (
			select max(wfbid) from weibo_spider.weibo_forward_blog
			group by uni_code);

-- 删除重复数据
delete from weibo_spider.weibo_forward_blog
	where wfbid not in  (
		select wfbid from tmp_fb);

drop table if exists tmp_fb;