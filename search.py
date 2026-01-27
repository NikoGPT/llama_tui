# search.py
import os

def find_models_smart(base_dir="models"):
    """Ищет модели ТОЛЬКО в папке проекта."""
    model_list = []
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        return model_list
    
    for root, dirs, files in os.walk(base_dir):
        # Пропускаем технические папки
        if any(x in root.lower() for x in ["venv", "bin", "__pycache__"]):
            continue
        
        # Ищем файлы с расширением .gguf
        ggufs = [f for f in files if f.endswith(".gguf") and "mmproj" not in f.lower()]
        
        for m in ggufs:
            m_path = os.path.join(root, m)
            
            # Проверяем, существует ли файл
            if not os.path.exists(m_path):
                continue
                
            # Ищем соответствующий mmproj файл
            mmprojs = [f for f in files if f.endswith(".gguf") and "mmproj" in f.lower()]
            proj_path = os.path.join(root, mmprojs[0]) if mmprojs else None
            
            # Проверяем, существует ли mmproj файл
            if proj_path and not os.path.exists(proj_path):
                proj_path = None
                
            model_list.append({
                "name": m,
                "path": os.path.abspath(m_path),
                "mmproj": os.path.abspath(proj_path) if proj_path else None
            })
    
    return model_list
