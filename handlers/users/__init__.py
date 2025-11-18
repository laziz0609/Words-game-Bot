import importlib

modules = [
    
    "help" ,
    "my_games",
    "play_game",
    "create_game",
    "change_name",    
    "start",   
]

routers = []

for module_name in modules:
    module = importlib.import_module(f".{module_name}", package=__name__)
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if attr_name.startswith("router") and hasattr(attr, "message"):
            routers.append(attr)
