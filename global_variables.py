app_data = None
ws = None

tokens = []
joined_tokens = []
blacklisted_tokens = []
quarantined_tokens = []
dmed_users = []

joins_failed = 0
joins_success = 0

messages_failed = 0
messages_sent = 0

ids_scraped_finished = 0
ids_scraped = 0

approximate_member_count = None
approximate_presence_count = None

successful_dm_limit = 0

valid_tokens = []
valid_tokens_count = 0

current_guild_info = None
current_version = 1.6