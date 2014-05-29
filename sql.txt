CREATE TABLE `hbc` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `address` varchar(16) DEFAULT NULL,
  `site` varchar(8) DEFAULT NULL,
  `passtime` datetime NOT NULL DEFAULT '2000-01-01 00:00:00' COMMENT '经过时间',
  `hpzl` char(4) DEFAULT NULL COMMENT '号牌种类',
  `hphm` char(10) DEFAULT '-' COMMENT '车牌号码',
  `fxbh` varchar(8) DEFAULT NULL COMMENT '方向',
  `wzlx` varchar(16) DEFAULT NULL COMMENT '违章类型',
  `cdbh` char(4) DEFAULT NULL COMMENT '车道编号',
  `fdjh` varchar(16) DEFAULT NULL COMMENT '发动机代号',
  `clsbdh` varchar(32) DEFAULT NULL COMMENT '车架号',
  `urlpath` varchar(64) DEFAULT NULL COMMENT '图片url路径',
  `imgpath` varchar(64) DEFAULT NULL COMMENT '图片本地路径',
  `banned` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`,`passtime`),
  KEY `index_passtime` (`passtime`) USING BTREE,
  KEY `index_hphm` (`hphm`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8
/*!50100 PARTITION BY RANGE (YEAR(passtime))
(PARTITION p0 VALUES LESS THAN (2018) ENGINE = InnoDB,
 PARTITION p1 VALUES LESS THAN (2022) ENGINE = InnoDB,
 PARTITION pMAX VALUES LESS THAN MAXVALUE ENGINE = InnoDB) */;