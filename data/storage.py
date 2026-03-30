import json
import os
import shutil

# =====================================================
# DATA FILE CONFIG
# =====================================================
DATA_FILE = "data.txt"
BACKUP_FILE = "data_backup.txt"


# =====================================================
# LOAD DATA
# =====================================================
def load_data():
    """
    Load user data from JSON file

    Returns:
        dict of user data
    """

    # Create file if missing
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            if not isinstance(data, dict):
                return {}

            return data

    except json.JSONDecodeError:
        print("⚠ Data file corrupted. Creating new file.")
        return {}

    except Exception as e:
        print("❌ Error loading data:", e)
        return {}


# =====================================================
# SAVE DATA
# =====================================================
def save_data(data):
    """
    Save user data safely to JSON file
    """

    try:
        # Backup existing file
        if os.path.exists(DATA_FILE):
            shutil.copy(DATA_FILE, BACKUP_FILE)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception as e:
        print("❌ Error saving data:", e)
        return False


# =====================================================
# GET USER
# =====================================================
def get_user(user_id):
    """
    Return user record or None
    """
    data = load_data()
    return data.get(user_id)


# =====================================================
# ADD USER
# =====================================================
def add_user(user_id, user_info):
    """
    Add new user to storage
    """

    data = load_data()

    if user_id in data:
        return False

    data[user_id] = user_info
    return save_data(data)


# =====================================================
# UPDATE USER
# =====================================================
def update_user(user_id, updated_info):
    """
    Update existing user info
    """

    data = load_data()

    if user_id not in data:
        return False

    data[user_id].update(updated_info)
    return save_data(data)


# =====================================================
# DELETE USER
# =====================================================
def delete_user(user_id):
    """
    Remove user from storage
    """

    data = load_data()

    if user_id not in data:
        return False

    del data[user_id]
    return save_data(data)


# =====================================================
# RESET DATABASE (Optional)
# =====================================================
def reset_data():
    """
    Clear all stored data
    """

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return True

    except Exception as e:
        print("❌ Reset failed:", e)
        return False