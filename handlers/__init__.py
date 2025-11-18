from . import admins, users

# ❗ Tartib bo‘yicha: admin birinchi, user keyin
routers = [
    *admins.routers,
    *users.routers,
]
