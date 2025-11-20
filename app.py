# app.py

import uvicorn

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Servidor iniciado correctamente")
    print("="*50)
    print("📱 Acceso local:      http://localhost:8000")
    print("🌐 Acceso red local:  http://0.0.0.0:8000")
    print("📚 Docs API:          http://localhost:8000/docs")
    print("="*50 + "\n")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",  # ← MANTÉN ESTO para acceso desde red
        port=8000,
        reload=True
    )