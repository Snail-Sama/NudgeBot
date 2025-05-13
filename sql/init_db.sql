DROP TABLE IF EXISTS goals;
CREATE TABLE goals (
	goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title	TEXT NOT NULL,
    description	TEXT,
	target	INTEGER NOT NULL,
	progress INTEGER DEFAULT 0,
	reminder TEXT DEFAULT 'N',
	"job"	BLOB,
)

CREATE INDEX idx_user_id ON goals(user_id ASC)