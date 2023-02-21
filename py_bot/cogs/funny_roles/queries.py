# Select Queries
SELECT_ROLE_AUTHOR_QUERY: str = """
    SELECT mbgr.id
        FROM member_bot_guild_role mbgr
        JOIN discord_member adm ON mbgr.author_member_id = adm.id
        JOIN discord_member vdm ON mbgr.victim_member_id = vdm.id
    WHERE 
        mbgr.role_id = %s AND
        adm.user_id = %s AND    
        vdm.user_id = %s           
"""

SELECT_GIVEN_ROLES_QUERY: str = """
    SELECT vdm.user_id, bgr.name
        FROM discord_member adm
        JOIN member_bot_guild_role mbgr ON mbgr.author_member_id = adm.id
        JOIN discord_member vdm ON vdm.id = mbgr.victim_member_id
        JOIN bot_guild_role bgr ON mbgr.role_id = bgr.id
    WHERE adm.user_id = %s
"""

SELECT_COUNT_GIVEN_ROLES_QUERY: str = """
    SELECT COUNT(*)
        FROM member_bot_guild_role
    WHERE author_member_id = %s
"""

SELECT_MEMBER_QUERY: str = """
    SELECT dm.id
        FROM discord_member dm
    WHERE dm.user_id = %s    
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

# Delete Queries
DELETE_ROLE_RELATION_QUERY: str = """
    DELETE FROM member_bot_guild_role mbgr
    WHERE mbgr.id = %s         
"""

DELETE_UNUSED_ROLE_QUERY: str = """
    DELETE FROM bot_guild_role bgr
    WHERE bgr.id = %s         
"""

