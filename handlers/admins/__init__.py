import importlib

# ❗ Faqat shu ro‘yxatdagi fayllardan routerlar yuklanadi
modules = [
    "notify",  
    "stats",
]

routers = []

for module_name in modules:
    module = importlib.import_module(f".{module_name}", package=__name__)
    # Fayl ichida "router" nomli obyekt(lar)ni avtomatik topamiz
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if attr_name.startswith("router") and hasattr(attr, "message"):
            routers.append(attr)
