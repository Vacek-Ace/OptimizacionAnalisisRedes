import os
import subprocess
import sys

def get_conda_env():
    env = os.environ.copy()
    python_dir = os.path.dirname(sys.executable)
    if os.name == 'nt':
        scripts_path = os.path.join(python_dir, 'Scripts')
    else:
        scripts_path = os.path.join(python_dir, 'bin')
    if os.path.exists(scripts_path):
        env['PATH'] = scripts_path + os.pathsep + env['PATH']
    return env

def check_env():
    print("=== VERIFICACION DEL ENTORNO ===")
    
    # Verificar que estamos ejecutando desde la raiz del proyecto
    if not os.path.exists("_quarto.yml"):
        print("[ERROR] Este script debe ejecutarse desde la raiz del proyecto.")
        return False
    else:
        print("[OK] Ejecutando desde la raiz del proyecto.")
        
    # Verificar archivos necesarios
    archivos = [
        "guia_estudio/guia_estudio.qmd",
        "guia_estudio/portada.html",
        "estilos.css"
    ]
    for archivo in archivos:
        if os.path.exists(archivo):
            print(f"[OK] {archivo} encontrado.")
        else:
            print(f"[ERROR] {archivo} NO encontrado.")
            return False
            
    # Verificar importacion de pypdf
    try:
        import pypdf
        print("[OK] pypdf instalado.")
    except ImportError:
        print("[ERROR] pypdf NO instalado. Por favor instalo en tu entorno de conda.")
        return False
        
    print("[OK] Verificacion del entorno completada con exito.\n")
    return True

def crear_portada():
    print("1. Generando portada con WeasyPrint...")
    
    dir_original = os.getcwd()
    os.chdir("guia_estudio")
    
    portada_content = """---
format:
  pdf:
    pdf-engine: weasyprint
    include-before-body: portada.html
    css: ../estilos.css
---
"""
    
    with open("portada_temp.qmd", "w", encoding="utf-8") as f:
        f.write(portada_content)
        
    try:
        # Renderizar portada
        subprocess.run(["quarto", "render", "portada_temp.qmd", "--output", "portada_temp.pdf", "--quiet"], env=get_conda_env(), check=True)
        if not os.path.exists("portada_temp.pdf"):
            raise FileNotFoundError("portada_temp.pdf no fue generado.")
        print("   [OK] Portada creada.")
    except Exception as e:
        print(f"   [ERROR] Creando portada: {e}")
        raise e
    finally:
        os.chdir(dir_original)

def crear_contenido():
    print("2. Creando contenido de la guia con LaTeX...")
    
    dir_original = os.getcwd()
    os.chdir("guia_estudio")
    
    # Leer contenido original
    with open("guia_estudio.qmd", "r", encoding="utf-8") as f:
        contenido_original = f.read()
        
    # Extraer el contenido libre de YAML original
    partes = contenido_original.split("---")
    if len(partes) >= 3:
        contenido_sin_yaml = "---".join(partes[2:])
    else:
        contenido_sin_yaml = contenido_original
        
    # Crear nuevo YAML para LaTeX (sin portada.html)
    yaml_latex = """---
lang: es
format:
  pdf:
    documentclass: scrreprt
    pdf-engine: pdflatex
    title-block-banner: false 
    toc: true
    toc-title: "Indice de contenidos"
    number-sections: true
    geometry:
      - margin=2.5cm
    fontsize: 11pt
---
"""
    
    with open("contenido_temp.qmd", "w", encoding="utf-8") as f:
        f.write(yaml_latex + "\n" + contenido_sin_yaml)
        
    try:
        # Renderizar con LaTeX
        subprocess.run(["quarto", "render", "contenido_temp.qmd", "--output", "contenido_temp.pdf"], env=get_conda_env(), check=True)
        if not os.path.exists("contenido_temp.pdf"):
            raise FileNotFoundError("contenido_temp.pdf no fue generado.")
        print("   [OK] Contenido creado.")
    except Exception as e:
        print(f"   [ERROR] Creando contenido: {e}")
        raise e
    finally:
        os.chdir(dir_original)

def unir_pdfs(nombre_salida="GuiaEstudioOptimizacionAnalisisRedes.pdf"):
    print("3. Uniendo PDFs...")
    
    dir_original = os.getcwd()
    os.chdir("guia_estudio")
    
    portada_path = "portada_temp.pdf"
    contenido_path = "contenido_temp.pdf"
    salida_path = nombre_salida
    
    if not os.path.exists(portada_path) or not os.path.exists(contenido_path):
        raise FileNotFoundError("Faltan archivos temporales PDF para unir.")
        
    try:
        from pypdf import PdfWriter
        
        writer = PdfWriter()
        writer.append(portada_path)
        writer.append(contenido_path)
        writer.write(salida_path)
        writer.close()
        
        if not os.path.exists(salida_path):
            raise FileNotFoundError("No se pudo crear el PDF final unido.")
            
        # Limpiar temporales
        temp_files = ["portada_temp.qmd", "portada_temp.pdf", "contenido_temp.qmd", "contenido_temp.pdf"]
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
                
        print("   [OK] PDFs unidos correctamente.")
        print("   [OK] Archivos temporales eliminados.")
    except Exception as e:
        print(f"   [ERROR] Al unir PDFs: {e}")
        raise e
    finally:
        os.chdir(dir_original)

def crear_guia_completa(nombre_salida="GuiaEstudioOptimizacionAnalisisRedes.pdf"):
    print("=== CREANDO GUIA DE ESTUDIO ===")
    if not check_env():
        return
        
    try:
        crear_portada()
        crear_contenido()
        unir_pdfs(nombre_salida)
        
        ruta_final = os.path.join("guia_estudio", nombre_salida)
        print("\n=== PROCESO COMPLETADO ===")
        print(f"[OK] Portada (WeasyPrint con HTML)")
        print(f"[OK] Contenido (LaTeX para calidad tipografica)")
        print(f"[OK] PDFs unidos correctamente")
        print(f"Archivo final: {ruta_final}")
        print(f"Tamano: {round(os.path.getsize(ruta_final)/1024/1024, 2)} MB")
    except Exception as e:
        print(f"\n[ERROR] En el proceso: {e}")

if __name__ == "__main__":
    crear_guia_completa()
