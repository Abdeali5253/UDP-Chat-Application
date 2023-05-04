# Description: This file contains all the constants used in the project.

# emoji_list is a list of all the emojis
emoji_list = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰", 
    "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "😏", "😒", 
    "😞", "😔", "😟", "😕", "🙁", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "🤬", "😡", 
    "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤥", "🙄", "😬", "😐", "😑", 
    "😶", "😇", "🙏", "💪", "👍", "👎", "👊", "✊", "🤛", "🤜", "🤞", "🤟", "🤘", "👌", "👈", "👉", 
    "👆", "👇", "☝️", "✋", "🤚", "🖐️", "🖖", "👋", "🤙", "💅", "👂", "👃", "👣", "👀", "👁️", "👅", 
    "👄", "💋", "👶", "👦", "👧", "👩", "👨", "👱", "👴", "👵", "👲", "👳", "🧕", "👮", "👷", "💂", "🕵️", 
    "👩‍⚕️", "👨‍⚕️", "👩‍🎓", "👨‍🎓", "👩‍🏫", "👨‍🏫", "👩‍⚖️", "👨‍⚖️", "👩‍🌾", "👨‍🌾", "👩‍🍳", "👨‍🍳", "👩‍🔧", "👨‍🔧", "👩‍🏭", "👨‍🏭", 
    "👩‍💼", "👨‍💼", "👩‍🔬", "👨‍🔬", "👩‍💻", "👨"]

# Packet size in bytes
PACKET_SIZE = 1024 

# Timeout in seconds
TIMEOUT = 1000000



from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode('utf-8'))

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode('utf-8')