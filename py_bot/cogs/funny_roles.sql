-- Adminer 4.8.1 MySQL 8.0.27 dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP TABLE IF EXISTS `bot_guild_role`;
CREATE TABLE `bot_guild_role` (
  `id` bigint NOT NULL COMMENT 'Discord Role ID',
  `name` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `discord_member`;
CREATE TABLE `discord_member` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guild_id` bigint NOT NULL COMMENT 'Discord Guild ID',
  `user_id` bigint NOT NULL COMMENT 'Discord User ID',
  `name` varchar(256) NOT NULL,
  `discriminator` varchar(128) DEFAULT NULL,
  `is_bot` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `member_bot_guild_role`;
CREATE TABLE `member_bot_guild_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `author_member_id` int NOT NULL,
  `victim_member_id` int NOT NULL,
  `role_id` bigint NOT NULL COMMENT 'Discord Role ID',
  PRIMARY KEY (`id`),
  KEY `role_id` (`role_id`),
  KEY `author_member_id` (`author_member_id`),
  KEY `victim_member_id` (`victim_member_id`),
  CONSTRAINT `member_bot_guild_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `bot_guild_role` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `member_bot_guild_role_ibfk_3` FOREIGN KEY (`author_member_id`) REFERENCES `discord_member` (`id`),
  CONSTRAINT `member_bot_guild_role_ibfk_4` FOREIGN KEY (`victim_member_id`) REFERENCES `discord_member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- 2021-12-15 17:28:39