import os

def find_models_smart(base_dir="models"):
    model_list = []
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    for root, dirs, files in os.walk(base_dir):
        if any(x in root.lower() for x in ["venv", "bin", "__pycache__"]):
            continue
            
        ggufs = [f for f in files if f.endswith(".gguf") and "mmproj" not in f.lower()]
        mmprojs = [f for f in files if f.endswith(".gguf") and "mmproj" in f.lower()]
        
        for m in ggufs:
            m_path = os.path.join(root, m)
            proj_path = os.path.join(root, mmprojs[0]) if mmprojs else None
            
            model_list.append({
                "name": m,
                "path": os.path.abspath(m_path),
                "mmproj": os.path.abspath(proj_path) if proj_path else None
            })
    return model_list
