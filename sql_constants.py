#!/usr/env/bin python3
SQL_STRINGS = {
    "CREATE_MESSAGE_TABLE": """CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        author INTEGER NOT NULL,
        channelid INTEGER,
        channelname TEXT,
        guildid INTEGER,
        clean_content TEXT,
        created_at TIMESTAMP
    ); """,

    "CREATE_ROLES_TABLE": """CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY,
        chirper INTEGER,
        chirper2 INTEGER,
        chirper3 INTEGER,
        chirper4 INTEGER,
        frozen INTEGER,
        youngling INTEGER
    ); """,

    "VOTERS": "SELECT author FROM messages WHERE channelid = ? AND created_at >= datetime('now', '-7 days') GROUP BY author HAVING COUNT(*) > ?;",
    
    "LEADERBOARD": "SELECT author, COUNT(id) FROM messages WHERE created_at >= datetime('now', '-7 days') AND author != 356878329602768897 AND author != ? AND guildid = ? GROUP BY author ORDER BY COUNT(id) DESC LIMIT ?;",
    
    "MAYOBOARD": "SELECT author, COUNT(author) FROM messages WHERE clean_content LIKE '%mayo%' AND channelid != 622383698259738654 AND author != ? AND guildid = ? GROUP BY author ORDER BY COUNT(author) DESC LIMIT ?;",
    
    "MOD_LOGS": "SELECT user, COUNT(id) FROM modlogs WHERE user = ? GROUP BY user ORDER BY COUNT(id) DESC;",
    
    "MOD_SCOREBOARD": "SELECT author, COUNT(author) FROM modlogs GROUP BY author ORDER BY COUNT(id) DESC;",
    
    "ADD_MESSAGE": "INSERT INTO messages(id,author,channelid,channelname,guildid,clean_content,created_at) VALUES(?,?,?,?,?,?,?)",
    
    "ADD_MODLOG": "INSERT INTO modlogs(id,author,channelid,channelname,guildid,clean_content,created_at,user,type) VALUES(?,?,?,?,?,?,?,?,?)",
    
    "WARN": "SELECT user, COUNT(id) FROM modlogs WHERE user = ? GROUP BY user  ORDER BY COUNT(id) DESC;",
    
    "MUTE": "SELECT user, COUNT(id) FROM modlogs WHERE user = ? GROUP BY user  ORDER BY COUNT(id) DESC;",

    "STORE_ROLE": "INSERT OR REPLACE INTO roles VALUES(?,?,?,?,?,?,?)",
    
    "RETRIEVE_ROLE": "SELECT chirper, chirper2, chirper3, chirper4 FROM roles WHERE id = ?;",
    
    "REPORTS":{
        "MONTH": [
            "SELECT COUNT(*) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-30 days')",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-30 days')"
        ],

        "FILTERWEEK": [
            "SELECT COUNT(*) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-7 days')",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-7 days')"
        ],
        
        "ALLWEEK": [
            "SELECT COUNT(*) FROM messages WHERE created_at >= datetime('now', '-7 days')",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE created_at >= datetime('now', '-7 days')"
        ],
        
        "CATWEEK": [
            "SELECT COUNT(*) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-7 days')",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-7 days')"
        ],
        
        "FILTERDAY": [
            "SELECT COUNT(*) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-1 days')",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-1 days')"
        ],
        
        "ALLDAY": [
            "SELECT COUNT(*) FROM messages WHERE created_at >= datetime('now', '-1 days')",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE created_at >= datetime('now', '-1 days')"
        ],
        
        "CATDAY": [
            "SELECT COUNT(*) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-1 days')",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-1 days')"
        ],
        
        "WEEK": [
            "SELECT COUNT(*) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-7 days')",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-7 days')"
        ],

        "ALL": [
            "SELECT COUNT(*) FROM messages WHERE channelid =?",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE channelid =?"
        ],
        
        "DAY": [
            "SELECT COUNT(*) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-1 days')",
            "SELECT COUNT(DISTINCT author) FROM messages WHERE channelid =? AND created_at >= datetime('now', '-1 days')"
        ]
    },
    


}
