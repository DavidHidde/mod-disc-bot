# Select Queries
SELECT_GIVEN_ROLES_QUERY: str = """
    SELECT vdm.user_id, bgr.name
        FROM discord_member adm
        JOIN member_bot_guild_role mbgr ON mbgr.author_member_id = adm.id
        JOIN discord_member vdm ON vdm.id = mbgr.victim_member_id
        JOIN bot_guild_role bgr ON mbgr.role_id = bgr.id
    WHERE adm.user_id = %s
"""

SELECT_MEMBER_QUERY: str = """
    SELECT dm.id
        FROM discord_member dm
    WHERE dm.user_id = %s    
"""

SELECT_ROLE_QUERY: str = """
    SELECT bgr.id
        FROM  bot_guild_role bgr
    WHERE bgr.name = %s
"""

# Insert Queries
CREATE_ROLE_QUERY: str = """
    INSERT INTO bot_guild_role (id, name)
    VALUES (%s, %s)          
"""

CREATE_ROLE_RELATION_QUERY: str = """
    INSERT INTO member_bot_guild_role (
        author_member_id, 
        victim_member_id, 
        role_id
    ) VALUES (%s, %s, %s)          
"""

CREATE_MEMBER_QUERY: str = """
    INSERT INTO discord_member (
        guild_id,
        user_id,
        name,
        discriminator,
        is_bot
    ) VALUES (%s, %s, %s, %s, %s)   
"""

CREATE_TABLES_IF_NOT_EXISTS_QUERY: str = """
    CREATE TABLE IF NOT EXISTS `bot_guild_role`
    (
        `id`   bigint       NOT NULL COMMENT 'Discord Role ID',
        `name` varchar(256) NOT NULL,
        PRIMARY KEY (`id`)
    ) ENGINE = InnoDB
      DEFAULT CHARSET = utf8mb4
      COLLATE = utf8mb4_0900_ai_ci;


    CREATE TABLE IF NOT EXISTS `discord_member`
    (
        `id`            int          NOT NULL AUTO_INCREMENT,
        `guild_id`      bigint       NOT NULL COMMENT 'Discord Guild ID',
        `user_id`       bigint       NOT NULL COMMENT 'Discord User ID',
        `name`          varchar(256) NOT NULL,
        `discriminator` varchar(128)          DEFAULT NULL,
        `is_bot`        tinyint      NOT NULL DEFAULT '0',
        PRIMARY KEY (`id`)
    ) ENGINE = InnoDB
      DEFAULT CHARSET = utf8mb4
      COLLATE = utf8mb4_0900_ai_ci;


    CREATE TABLE IF NOT EXISTS `member_bot_guild_role`
    (
        `id`               int    NOT NULL AUTO_INCREMENT,
        `author_member_id` int    NOT NULL,
        `victim_member_id` int    NOT NULL,
        `role_id`          bigint NOT NULL COMMENT 'Discord Role ID',
        PRIMARY KEY (`id`),
        KEY `role_id` (`role_id`),
        KEY `author_member_id` (`author_member_id`),
        KEY `victim_member_id` (`victim_member_id`),
        CONSTRAINT `member_bot_guild_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `bot_guild_role` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
        CONSTRAINT `member_bot_guild_role_ibfk_3` FOREIGN KEY (`author_member_id`) REFERENCES `discord_member` (`id`),
        CONSTRAINT `member_bot_guild_role_ibfk_4` FOREIGN KEY (`victim_member_id`) REFERENCES `discord_member` (`id`)
    ) ENGINE = InnoDB
      DEFAULT CHARSET = utf8mb4
      COLLATE = utf8mb4_0900_ai_ci;
"""

# Delete Queries
DELETE_ROLE_RELATION_QUERY: str = """
    DELETE FROM member_bot_guild_role mbgr
    WHERE mbgr.author_member_id = %s AND
        mbgr.victim_member_id = %s AND
        mbgr.role_id = %s     
"""

DELETE_UNUSED_ROLE_QUERY: str = """
    DELETE FROM bot_guild_role bgr
    WHERE bgr.id = %s         
"""
