import sqlite3

conn = sqlite3.connect("fracfocus.db")

conn.execute("CREATE INDEX IF NOT EXISTS idx_disclosure ON registry(DisclosureId)") # creates index for DisclosureId if not yet created
conn.execute("CREATE INDEX IF NOT EXISTS idx_state ON registry(StateName, DisclosureId)") # creates index for StateName and DisclosureID together if not yet created

conn.commit()
conn.close()