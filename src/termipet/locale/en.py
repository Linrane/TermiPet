"""English locale strings for TermiPet"""
STRINGS = {
    # ── Reusable data lookups ──
    "data": {
        "stages": {
            "egg": "Egg", "youth": "Youth", "teen": "Teen", "adult": "Adult",
            "peak": "Peak", "legend": "Legend", "ancient": "Ancient",
            # Reverse mappings (DB stores Chinese values)
            "蛋": "Egg", "幼年": "Youth", "少年": "Teen", "成年": "Adult",
            "巅峰": "Peak", "传奇": "Legend", "远古": "Ancient",
        },
        "stats": {
            "hunger": "Hunger", "happiness": "Happiness", "cleanliness": "Cleanliness",
            "health": "Health", "energy": "Energy", "intelligence": "Intelligence",
            "bond": "Bond", "constitution": "Constitution",
            # Reverse mappings
            "饱腹": "Hunger", "快乐": "Happiness", "清洁": "Cleanliness",
            "健康": "Health", "精力": "Energy", "智力": "Intelligence",
            "亲密": "Bond", "体质": "Constitution",
        },
        "personalities": {
            "brave": "Brave", "coward": "Cowardly", "playful": "Playful",
            "calm": "Calm", "gentle": "Gentle", "tsundere": "Tsundere",
            # Reverse mappings
            "勇敢": "Brave", "胆小": "Cowardly", "顽皮": "Playful",
            "沉稳": "Calm", "温柔": "Gentle", "傲娇": "Tsundere",
        },
        "talents": {
            "big_appetite": "Big Appetite", "explorer": "Explorer", "sweet_sleeper": "Sweet Sleeper",
            "social_star": "Social Star", "iron_stomach": "Iron Stomach", "self_heal": "Self-Heal",
            "genius_child": "Genius Child", "night_owl": "Night Owl",
            # Reverse mappings
            "大胃王": "Big Appetite", "探险家": "Explorer", "甜睡者": "Sweet Sleeper",
            "社交达人": "Social Star", "铁胃": "Iron Stomach", "自愈力": "Self-Heal",
            "天才儿童": "Genius Child", "夜猫子": "Night Owl",
        },
        "rooms": {
            "bedroom": "Bedroom", "kitchen": "Kitchen", "workshop": "Workshop",
            "garden": "Garden", "library": "Library",
            # Reverse mappings
            "卧室": "Bedroom", "厨房": "Kitchen", "工坊": "Workshop",
            "花园": "Garden", "图书室": "Library",
        },
        "rarities": {
            "common": "Common", "rare": "Rare", "legendary": "Legendary",
        },
        "item_types": {
            "consumable": "Food/Medicine", "material": "Material",
            "equipment": "Equipment", "collectible": "Collectible",
        },
        "directions": {
            "up": "Up", "down": "Down", "left": "Left", "right": "Right",
        },
        "battle": {
            "attack": "Attack", "defend": "Defend", "skill": "Skill",
            "win": "Victory", "lose": "Defeat", "draw": "Draw",
        },
        "skill_types": {
            "heal": "Heal", "treasure": "Treasure", "soothe": "Soothe",
            "combat": "Combat", "passive": "Passive", "explore": "Explore",
        },
        "quest_types": {
            "daily": "Daily", "weekly": "Weekly", "story": "Story",
            "cumulative": "Cumulative", "hidden": "Hidden",
        },
        "event_categories": {
            "exploration": "Exploration", "home_life": "Home Life", "social": "Social",
            "weather": "Weather", "growth": "Growth", "species": "Species",
        },
        "species": {
            "cat": "Feline Spirit", "dog": "Canine Spirit", "bird": "Avian Spirit",
            "mech": "Mech Spirit", "mystery": "Mystery Spirit",
        },
        "mood": {
            "happy": "Happy", "normal": "Normal", "sad": "Sad", "sick": "Sick",
        },
        "actions": {
            "learn": "Learn", "upgrade": "Upgrade",
        },
        "status": {
            "active": "Active", "dormant": "Dormant",
        },
        "yes": "Yes", "no": "No",
        "yes_no": "Yes / No",
        "not_learned": "Not learned",
        "locked": "Locked",
        "no_data": "No data. Please initialize game data first.",
        "unknown": "Unknown",
        "day_suffix": "d",
        "no_change": "No change",
        "no_pet": "No pet yet",
        "none": "None",
        "floor": "F",
        "level": "Lv",
        "max_level": "MAX",
        "event": "Event",
    },

    # ── Banner ──
    "banner": {
        "title": "✦ TermiPet 2.2  Terminal Spirit Companion ✦",
        "subtitle": "Guardian of digital life, writing spirit beast legends in the terminal",
    },

    # ── CLI help text ──
    "cli": {
        "description": "TermiPet 2.2 — Terminal Spirit Companion",
        "quick_start": "Quick Start:",
        "adopt_example": "pet adopt cat --name Fluffy     Adopt a feline spirit",
        "status_example": "pet status                    View pet status",
        "feed_example": "pet feed                      Feed your pet",
        "play_example": "pet play                      Play with your pet",
        "adventure_example": "pet adventure start           Start an adventure",
        "help_hint": "Use pet <command> --help for detailed usage.",
        "cmd_load_fail": "Command loading failed: {error}",
        "init_warning": "Initialization warning: {error}",
    },

    # ── Common messages ──
    "common": {
        "error_unexpected": "An unexpected error occurred: {error}",
        "cancelled": "Cancelled.",
        "confirm": "Are you sure?",
        "no_pet_adopt": "No pet yet! Use {cmd} to adopt a spirit companion!",
        "available_species": "Available species: cat, dog, bird, mech, mystery",
        "no_adventure": "No active adventure! Use pet adventure start to begin.",
        "no_active_adventure": "No active adventure. Use pet adventure start to begin one.",
        "pet_not_found": "No pet with ID {id}. Use pet list-pets to see all pets.",
        "switch_success": "Switched to \"{name}\".",
        "not_found": "✗ No pet with ID {id}. Use pet list-pets to see all pets.",
        "switch_success_check": "✓ Switched to \"{name}\".",
        "no_pets": "No pets yet.",
        "adopted_pets": "🐾 Adopted Spirits",
        "no_such_pet_id": "No pet with ID {pet_id}. Use pet list-pets to see all pets.",
    },

    # ── Table headers ──
    "headers": {
        "id": "ID",
        "name": "Name",
        "species": "Species",
        "stage": "Stage",
        "age": "Age",
        "status": "Status",
        "active": "Active",
        "dormant": "Dormant",
    },

    # ── Command: adopt ──
    "adopt": {
        "help": "Adopt a new spirit companion",
        "name_prompt": "Give your spirit companion a name",
        "name_default": "Nova",
        "has_pet_confirm": "You already have \"{name}\". Adopting a new pet will mark it as inactive. Continue?",
        "summoning": "Summoning {species} spirit...",
        "success_title": "✨ Adoption Complete ✨",
        "success_body": "Congratulations! You've adopted a {species_name} spirit!\n\nName: {name}\nPersonality: {personality}  Talent: {talent}\n\nIt's still an egg — wait patiently for it to hatch...\nUse pet status to check on it, pet feed to feed it.",
    },

    # ── Command: status ──
    "status": {
        "help": "View current pet status",
        "daily_events": "📬 {name} has {count} daily event(s)!",
        "daily_hint": "It did {n} thing(s) while you were away. Use pet daily to view.",
        "warning_header": "⚠ Stat Warning:",
        "hunger_low": "Hunger {val:.0f} — starving!",
        "health_low": "Health {val:.0f} — needs treatment!",
        "energy_low": "Energy {val:.0f} — exhausted!",
    },

    # ── Command: feed ──
    "feed": {
        "help": "Feed your pet",
        "full_warning": "{name} is already full — overfeeding will hurt!",
        "feeding": "Feeding {name}...",
        "result_title": "🍖 {name} enjoyed the meal!",
        "result_body": "Fed \"{item}\"\n{effects}",
        "normal_feed": "Regular feed complete",
        "health_warning": "{name}'s health is very low ({val:.0f}), use medicine soon!",
    },

    # ── Command: play ──
    "play": {
        "help": "Play with your pet",
        "max_happiness": "{name} is already over the moon happy — let it rest~",
        "playing": "Playing with {name}...",
        "result_title": "🎮 {name} had a great time!",
    },

    # ── Command: clean ──
    "clean": {
        "help": "Clean your pet",
        "already_clean": "{name} is already spotless — no need to wash again~",
        "cleaning": "Bathing {name}...",
        "result_title": "🛁 {name} is fresh and clean!",
    },

    # ── Command: sleep ──
    "sleep": {
        "help": "Let your pet rest (default 4h), range 0.5-12 hours",
        "zero_hours": "Sleep time must be greater than 0 hours.",
        "max_hours": "Maximum sleep time is 12 hours. Adjusted automatically.",
        "cant_sleep": "{name} is full of energy and can't sleep!",
        "sleeping": "{name} drifts into dreamland... ({hours:.1f}h)",
        "result_title": "💤 {name} slept {hours:.1f}h, refreshed!",
    },

    # ── Command: train ──
    "train": {
        "help": "Train / learn skills",
        "egg_warning": "The egg hasn't hatched yet! Wait until it hatches before training.",
        "training": "{name} is training hard on \"{skill}\"...",
        "result_title": "⚡ Skill {action} successful!",
        "result_body": "{action} skill \"{skill}\" Lv.{level}  Cost: {cost} skill pts\nRemaining skill pts: {points}",
    },

    # ── Command: skill list ──
    "skill_list": {
        "help": "View skill tree",
        "title": "✦ {name}'s Skill Tree  (Skill Pts: {points})",
        "col_name": "Skill",
        "col_type": "Type",
        "col_cost": "Cost",
        "col_level": "Level",
        "col_desc": "Description",
        "col_status": "Status",
        "not_learned": "Not learned",
        "hint": "Use pet train <skill> to learn skills",
    },

    # ── Command: home ──
    "home": {
        "status_help": "View home status",
        "upgrade_help": "Upgrade a room",
        "craft_help": "Craft an item",
        "recipes_help": "View available recipes",
        "title": "🏠 {name}'s Home",
        "col_room": "Room",
        "col_level": "Level",
        "col_status": "Status",
        "col_function": "Function",
        "locked": "Locked",
        "decor_score": "Decor Score: {score}",
        "upgrade_hint": "Use pet home upgrade <room> to upgrade rooms",
        "room_info_bedroom": "Recover energy, enhance sleep",
        "room_info_kitchen": "Cook food, make medicine",
        "room_info_workshop": "Craft equipment, toys",
        "room_info_garden": "Grow materials",
        "room_info_library": "Research skills, craft skill books",
        "unknown_room": "Unknown room '{room}'. Available rooms: {rooms}",
        "max_level": "\"{room}\" is already at max level {level}!",
        "no_coins": "Not enough coins! Need {need} coins, only have {have}.",
        "no_materials": "Not enough materials! Missing: {materials}",
        "upgrading": "Upgrading \"{room}\"...",
        "upgrade_success": "🏗️ Upgrade Complete!",
        "upgrade_result": "Spent {coins} coins, {remaining} remaining",
        "confirm_upgrade": "Upgrade \"{room}\" to Lv.{level} costs: {coins_cost} coins, {materials}. Confirm?",
        "egg_craft": "Egg can't use the workshop! Wait until it hatches.",
        "crafting": "Crafting \"{recipe}\"...",
        "craft_success": "🔨 Crafting Complete!",
        "craft_result": "Crafted \"[bold cyan]{result}[/bold cyan]\"\nObtained: [bold yellow]{output}[/bold yellow] × {qty}",
        "no_recipes": "No recipes available. Upgrade kitchen, workshop, or library to unlock more.",
        "recipes_title": "📜 Available Recipes",
        "col_recipe": "Recipe",
        "col_materials": "Materials",
        "col_output": "Output",
        "col_craftable": "Craftable",
        "craft_hint": "Use pet home craft <recipe> to craft items",
        "home_not_exist": "Home data doesn't exist. Contact the developer.",
        "home_not_exist2": "Home data doesn't exist.",
    },

    # ── Command: adventure ──
    "adventure": {
        "start_help": "Start an adventure",
        "move_help": "Move in the maze",
        "auto_help": "Auto explore",
        "retreat_help": "Retreat",
        "status_help": "View current adventure status",
        "has_adventure": "You have an active adventure (floor {floor}). Starting a new one will abandon current progress. Continue?",
        "continue_hint": "Use [bold]pet adventure move <direction>[/bold] to continue.",
        "entering": "Entering maze floor {depth}...",
        "entered": "Entered maze floor {floor}!",
        "move_hint": "Move with: [bold]pet adventure move w/a/s/d[/bold]\nReach exit [bold yellow]E[/bold yellow] for next floor, use [bold]pet adventure retreat[/bold] to retreat",
        "start_title": "🗺️ Adventure Begins!",
        "cannot_move": "Cannot move.",
        "wall_block": "Blocked by a wall.",
        "ko_retreat": "{name} has lost consciousness, auto-retreating...",
        "auto_start": "Auto-explore started, max {steps} steps...",
        "auto_step": "Step {step}: {reason}",
        "auto_step_prefix": "Step {step}",
        "auto_empty": "......",
        "floor_enter": "Entering floor {floor}!",
        "floor_enter_bold": "Entering Floor {floor}!",
        "no_adventure_hint": "No active adventure! Use [bold]pet adventure start[/bold] to begin.",
        "no_active_adventure_hint": "No active adventure. Use [bold]pet adventure start[/bold] to begin one.",
        "retreating": "Retreating...",
        "empty_handed": "Empty-handed",
        "retreat_success": "🏃 Retreat Successful",
        "retreat_from": "Retreated from floor {floor}!",
        "loot_title": "Loot:",
        "floor_title": "Entering Floor {floor}!",
        "col_event": "Event",
        "event_chest": "📦 Chest!",
        "event_trap": "⚠ Trap!",
        "event_dodge": "✨ Dodge!",
        "event_danger": "💀 Danger!",
        "event_battle": "⚔ Battle!",
        "event_puzzle": "🔮 Puzzle!",
        "event_exit": "🚪 Exit!",
        "event_shop": "🛒 Shop!",
        "event_story": "📖 Story!",
        "event_empty": "Event",
    },

    # ── Command: shop ──
    "shop": {
        "list_help": "View shop items",
        "buy_help": "Buy an item",
        "sell_help": "Sell an item",
        "inventory_help": "View inventory",
        "no_items": "No items available",
        "no_items_category": "No items in category: {category}.",
        "title": "🛒 Spirit Shop  {coins} Coins · {stardust} Stardust",
        "col_name": "Item",
        "col_type": "Category",
        "col_rarity": "Rarity",
        "col_buy": "Price",
        "col_sell": "Sell",
        "col_effect": "Effect",
        "buy_hint": "Use [bold]pet shop buy <item>[/bold] to buy, [bold]pet shop sell <item>[/bold] to sell",
        "buy_success": "✅ Purchase Complete",
        "buy_result": "Bought [bold cyan]{item}[/bold cyan] × {count}\nSpent [bold red]{cost}[/bold red] coins  Remaining: [bold yellow]{remaining}[/bold yellow]",
        "sell_success": "💰 Sold",
        "sell_result": "Sold [bold cyan]{item}[/bold cyan] × {count}\nEarned [bold green]{earned}[/bold green] coins  Balance: [bold yellow]{coins}[/bold yellow]",
        "empty_bag": "Your bag is empty!",
        "bag_title": "🎒 {name}'s Inventory",
        "col_item": "Item",
        "col_qty": "Qty",
        "col_equipped": "Equipped",
        "equipped": "✓",
    },

    # ── Command: social (quests/achievements/story/collection) ──
    "social": {
        "quests_help": "View quest list",
        "claim_help": "Claim quest reward",
        "achievements_help": "View achievements",
        "story_help": "View story fragments",
        "collection_help": "View collection cabinet",
        "reward_title": "🎁 Reward Claimed",
        "reward_result": "Claimed quest \"{name}\" reward!\n[bold yellow]+{coins} coins[/bold yellow]  [bold cyan]+{stardust} stardust[/bold cyan]",
        "no_quests": "No quest data.",
        "col_quest": "Quest",
        "col_desc": "Description",
        "col_progress": "Progress",
        "col_reward": "Reward",
        "col_status": "Status",
        "claimed": "Claimed",
        "claimable": "Claimable!",
        "daily_title": "📅 Daily Quests",
        "weekly_title": "📆 Weekly Quests",
        "claimable_hint": "{count} quest(s) ready to claim!\nUse [bold]pet quests --claim <quest_key>[/bold] to claim",
        "ach_title": "🏆 Achievements  Unlocked {count}/{total}",
        "col_ach": "Achievement",
        "col_ach_type": "Type",
        "unlocked": "✓ Unlocked",
        "no_stories": "No story fragments unlocked yet.\nAdventure and grow to unlock more stories...",
        "invalid_fragment": "Invalid fragment number '{idx}'. Enter a number between 1 and {total}.",
        "story_title": "📚 Story Fragments  Unlocked {count}/{total}",
        "read_status": "Read",
        "new_status": "★ New",
        "story_hint": "Use [bold]pet story --read <number>[/bold] to read story fragments",
        "collection_title": "✦ {name}'s Collection ✦",
        "empty_collection": "The cabinet is empty... Complete achievements to collect badges!",
        "ach_count": "Achievements: {count}",
        "story_count": "Story fragments: {count}",
    },

    # ── Command: daily ──
    "daily": {
        "view_help": "View daily events",
        "read_help": "Read event details",
        "clear_help": "Mark all as read",
        "no_events": "No daily event records yet. Leave for a while and your pet will act on its own!",
        "no_unread": "No unread daily events. Use pet daily --all to view history.",
        "title": "📖 {name}'s Daily Events",
        "unread_count": "unread",
        "col_num": "#",
        "col_time": "Time",
        "col_category": "Category",
        "col_event_title": "Title",
        "col_summary": "Summary",
        "col_status": "Status",
        "new_tag": "New",
        "read_tag": "Read",
        "view_hint": "Use pet daily read <number> for details",
        "clear_hint": "pet daily clear to mark all read",
        "invalid_num": "Invalid number {idx}. There are {total} event records.",
        "detail_title": "📖 Event Detail #{idx}",
        "category_label": "Category:",
        "time_label": "Time:",
        "effect_label": "Effect:",
        "effect_title": "Event Details",
        "coins": "Coins",
        "stardust": "Stardust",
        "no_change": "No stat changes",
        "unknown_time": "Unknown time",
        "cleared": "Marked {count} daily event(s) as read.",
        "nothing_unread": "No unread daily events.",
    },

    # ── Core: pet_manager ──
    "pet_manager": {
        "no_pet": "No pet yet! Use pet adopt to adopt a spirit companion first.",
        "unknown_species": "Unknown species '{species}'.\nAvailable species: {species_list}",
        "empty_name": "Pet name cannot be empty!",
        "long_name": "Pet name cannot exceed 20 characters!",
        "no_item": "No '{item}' in your bag. Buy or craft it first.",
        "not_food": "'{item}' is not food and cannot be fed to your pet.",
        "too_tired": "{name} is too tired, energy at {energy:.0f}! Let it rest first.",
        "no_coins": "Not enough coins! Need {need} coins, only have {have}.",
        "no_stardust": "Not enough stardust! Need {need} stardust, only have {have}.",
    },

    # ── Core: adventure ──
    "adventure_core": {
        "egg_only": "The egg hasn't hatched yet, can't go adventuring!",
        "too_tired": "{name} is too tired... can't enter the maze!",
        "low_health": "{name}'s health is too low... entering the maze is too dangerous!",
        "rest_hint": "Use pet sleep 4 to let it rest.",
        "heal_hint": "Feed it and use medicine to restore health.",
        "no_adventure": "No active adventure! Use pet adventure start to begin.",
        "bad_direction": "Invalid direction '{direction}'. Use w/a/s/d or up/down/left/right.",
        "wall": "Blocked by a wall.",
        "wall_ahead": "Wall ahead!",
        "energy_out": "{name} is out of energy, auto-explore paused.",
        "health_critical": "{name} is critically wounded, auto-explore stopped!",
        "shop_found": "Found a maze shop! Use pet shop list to view items.",
        "empty_corridor": "An empty corridor...",
        "coins_found": "Coins +{amount}",
        "stardust_found": "Stardust +{amount}",
        "item_found": "Obtained {item}×{qty}",
        "chest_opened": "Opened a chest!",
        "trap_dodged": "Triggered a trap but nimbly dodged it!",
        "trap_ko": "Trap! Dealt {damage} damage, {name} lost consciousness... auto-retreat!",
        "trap_hit": "Triggered a trap! Lost {damage} health (remaining: {health:.0f})",
        "draw_result": "Draw! Both sides took minor damage, gained {coins} coins",
        "win_result": "Victory! Gained {exp} EXP, {coins} coins",
        "lose_result": "Defeat! Lost {damage} health (remaining: {health:.0f})",
        "ko_suffix": ", {name} lost consciousness... auto-retreat!",
        "next_floor": "Entering floor {floor}! Gained {exp} exploration EXP.",
        "story_found": "Discovered the story fragment \"{title}\"!",
        "puzzle_wrong": "Wrong puzzle answer... lost a small amount of health.",
    },

    # ── Core: economy ──
    "economy": {
        "not_in_shop": "'{item}' is not in the shop. Use pet shop list to see available items.",
        "not_in_bag": "'{item}' is not in your bag.",
        "equipped_cant_sell": "'{item}' is currently equipped, unequip it first.",
        "no_equipment": "No equipment '{item}' in your bag.",
        "not_equipped": "'{item}' is not equipped or doesn't exist.",
    },

    # ── Core: crafting ──
    "crafting": {
        "unknown_recipe": "Unknown recipe '{recipe}'.\nAvailable: {recipes}",
        "no_home": "Home data error. Please reinitialize.",
        "room_level_low": "Need {room} level {need}, currently at level {have}.",
        "room_upgrade_hint": "Use pet home upgrade {room} to upgrade.",
        "no_materials": "Not enough materials! Missing: {materials}",
        "bad_output": "Recipe data error: output item '{item}' doesn't exist.",
    },

    # ── Core: quests ──
    "quests_core": {
        "not_found": "Quest '{key}' doesn't exist.",
        "not_done": "Quest \"{name}\" not complete ({progress}/{target}).",
        "already_claimed": "Quest \"{name}\" reward already claimed.",
    },

    # ── Core: skill_system ──
    "skill_system": {
        "species_only": "Skill \"{name}\" is exclusive to {species} species.",
        "egg_only": "Your pet is still in its egg! Wait until it hatches.",
        "max_level": "Skill \"{name}\" is already at max level 5!",
        "no_points": "Not enough skill points! Learning \"{name}\" needs {need} pts, only have {have}.\nEarn more through interaction, adventure, and growth.",
    },

    # ── Display: status_panel ──
    "status_panel": {
        "title": "{name}'s Status",
        "live_title": "Live Status — Press Ctrl+C to exit",
        "live_countdown": "Countdown {remaining}s | Ctrl+C to exit",
        "live_exited": "Exited live status mode.",
        "pet_lost": "Pet data lost",
        "label_species": "Species",
        "label_stage": "Stage",
        "label_personality": "Personality",
        "label_talent": "Talent",
        "label_age": "Age",
        "label_exp": "EXP",
        "label_skill_points": "Skill Pts",
        "unknown": "Unknown",
        "coins_label": "Coins",
        "stardust_label": "Stardust",
        "stats_panel": "Stats",
        "info_panel": "Info",
        "mood": "Mood",
        "hunger_status": "Hunger",
        "last_updated": "Updated {minutes}min ago",
    },

    # ── Display: maze_ui ──
    "maze_ui": {
        "title": "Maze — Floor {floor}",
        "start": "Start",
        "exit": "Exit",
        "chest": "Chest",
        "trap": "Trap",
        "monster": "Monster",
        "puzzle": "Puzzle",
        "shop": "Shop",
        "loot_title": "✨ Loot:",
    },

    # ── Daily Events ──
    "daily_events": {
        # Exploration
        "garden_bug_hunt": {"title": "Garden Bug Hunt", "summary": "{name} chased butterflies in the garden and caught a data bug!", "detail": "{name} snuck into the garden and crept through the flowers for a full quarter-hour. Finally, it pounced on a shimmering butterfly — but the butterfly flew away, and a blue data bug was trapped under its paw instead!"},
        "stream_walk": {"title": "Data Stream Stroll", "summary": "{name} walked along the data stream and found some shiny coins.", "detail": "{name} strolled slowly along the data stream, its reflection shimmering in the clear data flow. Suddenly, golden sparkles appeared in the water — a small pile of coins wedged between data stones! {name} worked hard to pry them out."},
        "wall_escape": {"title": "Wall-Climbing Adventure", "summary": "{name} snuck over the boundary wall! You caught it, but it looks proud.", "detail": "While you weren't looking, {name} found a data crevice and slipped right out. When it came back, its fur was covered in strange fragments but its eyes sparkled with thrill — it says it saw sights beyond imagination beyond the wall."},
        "neighbor_visit": {"title": "Visiting Neighbors", "summary": "{name} visited the neighbor spirit and brought back a pack of snacks.", "detail": "{name} knocked on the neighbor spirit's door. While both owners chatted, {name} and the neighbor exchanged their treasured snacks in the corner. It came back with puffed cheeks — clearly had quite a feast."},
        "chase_butterfly": {"title": "Chasing Butterflies", "summary": "{name} chased a data butterfly all over the yard, panting but smiling.", "detail": "A blue data butterfly flew across the yard and {name}'s eyes instantly lit up. It leaped and pounced left and right — never caught it once, but its laughter echoed across the home. Finally it collapsed on the grass, watching the butterfly's silhouette, and sighed contentedly."},
        "data_rift_edge": {"title": "Edge of the Data Rift", "summary": "{name} curiously approached the data rift at the home boundary, sensing strange energy.", "detail": "There's a faint data rift at the edge of the home, usually sealed by a barrier. {name} crept close and felt a faint pulse from within. Tentatively, it reached out a paw — a pale blue glow flashed, and its intelligence seemed to grow."},
        # Home life
        "kitchen_snack": {"title": "Kitchen Snack Raid", "summary": "{name} snuck into the kitchen and fished out a pack of snacks.", "detail": "While you weren't looking, {name} tiptoed into the kitchen. It smelled the aroma of snacks hidden in the cabinet and, through sheer persistence (and nimble paws), pried the cupboard open. After a satisfying feast, it wiped its mouth — and thoughtfully closed the cabinet door."},
        "bedroom_roll": {"title": "Bedroom Rolling", "summary": "{name} rolled joyfully on the bedroom carpet, making a huge mess.", "detail": "{name} took advantage of the empty bedroom and rolled around ecstatically on the soft carpet. Three rolls left, three rolls right, and finally belly-up, sprawled out like a pancake. By the time you returned, the carpet had been rolled into an abstract art piece."},
        "garden_mess": {"title": "Garden Mess", "summary": "{name} played in the garden and accidentally knocked over several flower pots.", "detail": "{name} was so engrossed in chasing butterflies that it didn't notice the flower pots below. *Crash* — one, two, three... When it finally realized, the garden was a mess. {name} lowered its head in guilt and carefully tried to put the flowers back."},
        "workshop_invent": {"title": "Workshop Invention", "summary": "{name} tinkered in the workshop and claimed to have invented an 'auto-feeder'.", "detail": "{name} somehow learned to use the workshop tools. It cobbled together scrap parts and materials into a bizarre contraption. Though it proudly called it an 'auto-feeder', the device only squeaked 'creak' and fell apart during testing... but {name} didn't look discouraged at all."},
        "library_nap": {"title": "Library Nap", "summary": "{name} fell asleep in the library with a skill book pressed against its face.", "detail": "{name} carried a thick skill book into the library, solemnly declaring it would 'enrich itself'. But within ten minutes its eyelids began drooping... Finally it sprawled across the book, fast asleep, drool dampening the pages."},
        # Social
        "neighbor_fight": {"title": "Neighbor Feud", "summary": "{name} argued with the neighbor spirit over territory.", "detail": "A wild spirit invaded the area near the home, and {name} immediately perked up its ears and charged out. The neighbor spirit also arrived, drawn by the commotion, and both sides loudly debated the 'territory'. They eventually reached a complex border agreement — but by the next day {name} had forgotten what it agreed to."},
        "neighbor_makeup": {"title": "Making Up", "summary": "{name} went to apologize to the neighbor, bringing a small bag of coins as a gift.", "detail": "After their last argument, {name} realized it had been too aggressive. It counted a small bag of coins from its stash and carried it to the neighbor's door. The two spirits stood face to face for a long moment, then smiled at the same time — friendship restored under the sunset."},
        "gift_from_neighbor": {"title": "Neighbor's Gift", "summary": "The neighbor spirit sent {name} a small gift.", "detail": "A small package appeared at the door, tied with the neighbor spirit's ribbon. {name} carefully opened it — a finely polished data fragment inside, with a note: 'An apology gift for last time! Stop stealing my territory!'"},
        "teach_dance": {"title": "Dance Teacher", "summary": "{name} volunteered as a dance teacher, instructing the garden critters.", "detail": "{name} wiggled around in the garden, surrounded by a circle of curious critters. Though its dance moves could only be described as... 'unique', the critters watched with fascination and clumsily tried to follow. The scene was very joyful."},
        "data_plaza_perform": {"title": "Data Plaza Performance", "summary": "{name} gave an impromptu performance in the data plaza, drawing a crowd.", "detail": "The data plaza was especially lively today — {name} appeared out of nowhere and started an impromptu show in the center. It did somersaults, imitated various animal sounds, drawing cheers. It bowed proudly at the end."},
        # Weather
        "rainy_cold": {"title": "Caught a Cold in the Rain", "summary": "A data rainstorm hit and {name} got soaked before finding shelter.", "detail": "Ice-blue data rain suddenly poured down. {name} was playing in the garden and was drenched before reaching the house. It sneezed and curled up, shivering. When you returned, it looked at you with pitiful eyes, data raindrops still on its nose."},
        "sunny_charge": {"title": "Sunbathing Recharge", "summary": "Rare good weather — {name} basked comfortably on the windowsill all afternoon.", "detail": "Sunlight streamed through the data barrier, forming a golden patch. {name} discovered this perfect spot and lay motionless for hours. Its fur gleamed in the sunlight, looking freshly polished."},
        "thunder_scared": {"title": "Scared by Thunder", "summary": "A loud thunderclap made {name} dive under the blankets.", "detail": "An earth-shaking thunderclap suddenly echoed through the data world — a data storm was passing. {name} jumped three feet in the air, then dashed into the bedroom at lightspeed, wrapping itself head to tail in the blanket. It shivered underneath until the thunder completely faded."},
        "snow_snowman": {"title": "Snow Spirit", "summary": "A data snowfall came, and {name} built a tiny snow spirit in the yard.", "detail": "Pure white data snowflakes drifted down, and {name} was ecstatic. It rolled two snowballs of different sizes, put them together, used two data stones for eyes — a mini snow spirit was born! {name} circled its creation several times, looking very proud."},
        # Growth
        "weird_dream": {"title": "Strange Dream", "summary": "{name} had a very strange dream and sat stunned for a while after waking.", "detail": "{name} made strange sounds in its sleep — sometimes deep, sometimes high-pitched. When it woke, it looked around dazedly as if still lost in the dream. Though it couldn't describe what it dreamed, you sensed a new depth in its eyes."},
        "learn_new_trick": {"title": "Self-taught", "summary": "{name} figured out a new move by itself! A bit clumsy but very cute.", "detail": "While you were away, {name} practiced repeatedly in front of the mirror. It first tried standing up and walking — failed. Then tried spinning and jumping — also failed. Finally it invented a unique move: spin three times then pretend to faint. Simple, but it looked extremely satisfied with its 'original creation'."},
        "mirror_practice": {"title": "Mirror Expressions", "summary": "{name} somehow got a mirror and practiced various expressions in front of it.", "detail": "When you returned, {name} was making funny faces at the mirror. It smiled, glared, stuck out its tongue — then startled itself upon seeing its own reflection. This spontaneous 'expression management class' made it look even more sentient."},
        "diary_writing": {"title": "Secret Diary", "summary": "You found {name} scribbling on paper with clumsy handwriting.", "detail": "You crept closer and found {name} sprawled on the desk, awkwardly gripping a pen with its paw, writing something. You leaned in — a crooked drawing of you and it, with words beside it (probably): 'Owner not home today, but I will be a good kid.' Reading this, you decided not to disturb."},
        "peek_code": {"title": "Peeking at Your Code", "summary": "{name} crouched in front of the screen watching your code with a reviewer's expression.", "detail": "{name} jumped onto your workstation and stared intently at the scrolling code on the screen. It tilted its head and watched for a long time, then tapped the keyboard with its paw — the cursor landed right next to a bug. {name} turned to look at you, its eyes saying 'your code needs optimization'."},
        # Species: cat
        "cat_catch_mouse": {"title": "Caught a Data Mouse!", "summary": "{name} demonstrated feline instincts and successfully caught a data mouse.", "detail": "At 3 AM, {name}'s pupils suddenly dilated — it spotted an intruder! A green data mouse was stealing snacks from the kitchen. {name} lowered its body, tail gently swaying, then pounced with astonishing speed. The battle lasted five seconds, ending with the data mouse dropped at your feet. {name} looked extremely proud."},
        "cat_keyboard_nest": {"title": "Keyboard Cat Bed", "summary": "{name} sprawled on your keyboard and refused to leave, claiming 'it's the warmest spot'.", "detail": "Your keyboard radiates a gentle warmth — the perfect cat bed for {name}. It jumped on, spun three times, and curled into a perfect ball, eyes closed. You tried to move it, but it immediately opened its eyes with a displeased 'meow'. You ended up typing on your phone from the sidelines."},
        # Species: dog
        "dog_dig_hole": {"title": "Dug a Giant Hole", "summary": "{name} dug a deep hole in the garden, then looked at you innocently.", "detail": "The digging instinct of a canine spirit is unstoppable. {name} detected 'treasure' in the garden corner (actually data cables) and began frantically digging. When it stopped, a half-meter deep pit sat before it. It crouched by the edge, tail wagging furiously, eyes screaming 'praise me'."},
        "dog_steal_slipper": {"title": "Stole Your Slipper", "summary": "Your slipper vanished — found in {name}'s bed, being used as a pillow.", "detail": "Here we go again. You clearly remember the slippers being at the door, but now only one remains. Following the scent, you found {name}'s bed — both slippers neatly arranged beside its pillow, treated as some kind of precious collection. {name} saw you discovered its secret and immediately tried to hide the slippers under itself."},
        # Species: bird
        "bird_roof_sing": {"title": "Rooftop Singing", "summary": "{name} flew to the rooftop and sang a 'song' to the sunset.", "detail": "At dusk, {name} fluttered its wings and flew to the highest point of the home. It lifted its head and let out a long call — though 'song' is generous (more like a mix of data noise and bird calls), the silhouette against the sunset was genuinely beautiful. The neighbor spirits all fell quiet, 'enjoying' the impromptu concert."},
        "bird_steal_seed": {"title": "Stole the Seeds", "summary": "{name} pecked up every seed you had just planted in the garden.", "detail": "The seeds you carefully sowed hadn't even sprouted before {name} found them. 'What a great snack!' it thought. So it pecked them up one by one. By the time it burped contentedly, the garden beds had been overturned completely."},
        # Species: mech
        "mech_selfcheck": {"title": "System Self-Check Complete", "summary": "{name} performed a full diagnostic and gave itself a system upgrade.", "detail": "{name} activated its built-in diagnostic program. Test items scrolled across its screen: Body integrity ✓, Power system ✓, Data storage ✓, Logic unit ✓... All passed. It nodded approvingly, then secretly applied a small patch — 'self-optimization' complete."},
        "mech_short_circuit": {"title": "Short Circuit!", "summary": "{name} accidentally touched water, sparks flew — but it repaired itself quickly.", "detail": "{name} was watering the garden and didn't notice data water flowing into its joint gaps. 'Zzzt — pop!' A blue-white spark flashed, and {name}'s left eye briefly went dark. But it quickly activated self-repair and was back to normal in three minutes. Though it pretended nothing happened, you noticed it discreetly avoiding all water sources."},
        # Species: mystery
        "mystery_portal": {"title": "Opened a Portal", "summary": "{name} briefly opened a portal, glimpsing another dimension.", "detail": "{name} closed its eyes, the runes on its forehead beginning to glow faintly. Space twisted and folded before it — a purple rift appeared. Through it, a strange world of pure data could be faintly seen. But the rift closed after only a few seconds. {name} opened its eyes, deep in thought."},
        "mystery_future": {"title": "Read Future Fragments", "summary": "{name}'s talent let it capture data fragments from the future.", "detail": "The flow of time occasionally cracks in {name}'s perception. Today it touched one — fragmentary future images flashed through its mind: you and it standing side by side beneath a starry sky, surrounded by countless points of light. The vision vanished in an instant, but the warmth lingered."},
    },

    # ── Random events ──
    "events": {
        "surprise_finding": {"title": "Surprise Finding", "desc": "{name} found some shiny coins in the corner!"},
        "material_rain": {"title": "Material Shower", "desc": "{name} dug up some useful material fragments."},
        "happy_moment": {"title": "Happy Moment", "desc": "{name} chased the cursor on screen with pure joy!"},
        "energy_burst": {"title": "Energy Burst", "desc": "{name} suddenly perked up, as if recharged!"},
        "nightmare": {"title": "Nightmare", "desc": "{name} made strange sounds in its sleep... seems uncomfortable."},
        "indigestion": {"title": "Indigestion", "desc": "{name} seems to have eaten something wrong. Its stomach is upset."},
        "epiphany": {"title": "Epiphany", "desc": "{name} suddenly had an insight, +1 Skill Point!"},
        "mystery_gift": {"title": "Mystery Gift", "desc": "A mysterious package appeared at the door with something special inside..."},
    },

    # ── Skills ──
    "skills": {
        "quick_heal": {"name": "First Aid", "desc": "Quickly recover a small amount of health"},
        "treasure_nose": {"name": "Treasure Nose", "desc": "Easier to find chests during adventures"},
        "comfort_song": {"name": "Comfort Song", "desc": "Extra happiness recovery when soothing"},
        "battle_stance": {"name": "Battle Stance", "desc": "Gain defense bonus when entering battle"},
        "night_hunter": {"name": "Night Hunter", "desc": "Double EXP from nighttime adventures"},
        "forager": {"name": "Forager", "desc": "Automatically gain a small amount of food materials daily"},
        "sharp_mind": {"name": "Sharp Mind", "desc": "Intelligence growth accelerated"},
        "tough_skin": {"name": "Tough Skin", "desc": "Constitution cap +10"},
        "lucky_star": {"name": "Lucky Star", "desc": "Good random event chance +20%"},
        "shadow_step": {"name": "Shadow Step", "desc": "Trap trigger rate reduced by 30%"},
        "purr_therapy": {"name": "Purr Therapy", "desc": "Extra +10 health recovery during sleep"},
        "loyal_guard": {"name": "Loyal Guard", "desc": "30% chance to counterattack when hit"},
        "nose_track": {"name": "Tracking", "desc": "Maze map vision range +1 tile"},
        "sky_view": {"name": "Sky View", "desc": "See the entire maze floor map"},
        "melody": {"name": "Melody", "desc": "Happiness recovery +15 during play"},
        "overclock": {"name": "Overclock", "desc": "Battle win rate +25%"},
        "self_repair": {"name": "Self-Repair", "desc": "Auto-recover 5 health per hour"},
        "void_step": {"name": "Void Step", "desc": "Random teleport at the start of each adventure"},
        "ancient_pulse": {"name": "Ancient Pulse", "desc": "All stat decay rate -20%"},
    },

    # ── Quests ──
    "quests": {
        "daily_feed": {"name": "Today's Feeding", "desc": "Feed your pet 3 times today"},
        "daily_play": {"name": "Happy Time", "desc": "Play 2 times today"},
        "daily_clean": {"name": "Clean Freak", "desc": "Clean your pet once today"},
        "daily_adventure": {"name": "Adventure Time", "desc": "Go on 1 adventure today"},
        "weekly_craft": {"name": "Craftsman's Heart", "desc": "Craft items 5 times this week"},
        "weekly_maze5": {"name": "Abyss Explorer", "desc": "Reach maze floor 5 this week"},
        "weekly_bond": {"name": "Soul Bond", "desc": "Increase bond by 20 points this week"},
    },

    # ── Achievements ──
    "achievements": {
        "first_adopt": {"name": "First Adoption", "desc": "Adopted your first spirit companion"},
        "first_adventure": {"name": "First Journey", "desc": "Entered the maze for the first time"},
        "stage_adult": {"name": "Coming of Age", "desc": "Pet grew to adult stage"},
        "stage_legend": {"name": "Legend Arrives", "desc": "Pet grew to legend stage"},
        "stage_ancient": {"name": "Ancient Awakening", "desc": "Pet grew to ancient stage"},
        "feed_100": {"name": "Century Feeder", "desc": "Fed your pet 100 times"},
        "adventure_50": {"name": "Veteran Explorer", "desc": "Completed 50 adventures"},
        "maze_floor10": {"name": "Abyss Floor 10", "desc": "Reached maze floor 10"},
        "full_skills": {"name": "Full Skills", "desc": "Learned all general skills"},
        "rich_1000": {"name": "Petty Rich", "desc": "Coins reached 1000"},
        "health_0": {"name": "Near Death", "desc": "Health hit 0 then recovered"},
        "night_adventure": {"name": "Night Owl", "desc": "Went on an adventure at midnight"},
        "craft_legend": {"name": "Legendary Craftsman", "desc": "Crafted a legendary item"},
    },

    # ── Stories ──
    "stories": {
        "prologue_1": {"title": "The Rift's Beginning", "content": "On the day the data rift appeared at the system boundary, the first spirit opened its eyes from the void... It looked at you as if recognizing something."},
        "prologue_2": {"title": "Digital Life", "content": "Spirits are not ordinary data packets. They have will, emotion, and sometimes breathe softly in the late-night terminal."},
        "growth_1": {"title": "Hatching", "content": "The first crack appeared on the eggshell. The life inside waits for the right moment."},
        "growth_2": {"title": "Youthful Days", "content": "Little one learned its first skill — tapping the keyboard with its tail, making tinkling sounds."},
        "growth_3": {"title": "Adolescence", "content": "It began to grow curious about the maze. Every time you open the adventure interface, it crowds around to stare."},
        "growth_4": {"title": "Adult's Promise", "content": "\"Guardian,\" it spoke for the first time, voice echoing like circuits, \"thank you.\""},
        "maze_1": {"title": "Abyss Entrance", "content": "The first floor of the maze drifts with data corruption. Paw prints of an ancient spirit are carved into the stone slabs."},
        "maze_5": {"title": "The Secret of Floor 5", "content": "In a hidden corner of the fifth floor, you discovered a broken monument: 'A predecessor was here, I have reached —' the rest is lost."},
        "maze_10": {"title": "Abyss Core", "content": "At the center of the tenth floor, a portal of light awaits. Ancient chanting echoes from within, like primordial code running."},
        "species_cat": {"title": "The Cat's Secret", "content": "Feline spirits come from the shadow layer of data rifts. They move between light and darkness, seeing what others cannot."},
        "species_mech": {"title": "Mechanical Heart", "content": "Mech spirits are abandoned ancient programs, their steel shells wrapped around a core longing for understanding."},
        "hidden_1": {"title": "??????????", "content": "\"If one day I disappear, please remember — we once existed together in this terminal.\""},
    },

    # ── Species descriptions ──
    "species_desc": {
        "cat": "From the shadow layer of data rifts — agile, mysterious, adept at dodging traps",
        "dog": "Loyal and brave, strong in combat, skilled at tracking",
        "bird": "Soars above data streams — broad vision, can overview the entire maze",
        "mech": "Fragments of ancient programs, soft core wrapped in steel",
        "mystery": "An existence of unknown origin, possessing extraordinarily powerful ancient force",
    },
}
