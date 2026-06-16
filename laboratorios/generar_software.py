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
    print("=== VERIFICACIÓN DEL ENTORNO ===")
    if not os.path.exists("_quarto.yml"):
        print("[ERROR] Este script debe ejecutarse desde la raíz del proyecto.")
        return False
    
    archivos = [
        "laboratorios/software_utilizado.qmd",
        "laboratorios/portada.html",
        "estilos.css"
    ]
    for archivo in archivos:
        if os.path.exists(archivo):
            print(f"[OK] {archivo} encontrado.")
        else:
            print(f"[ERROR] {archivo} NO encontrado.")
            return False
            
    try:
        import pypdf
        print("[OK] pypdf instalado.")
    except ImportError:
        print("[ERROR] pypdf NO instalado. Por favor instálalo en tu entorno de conda.")
        return False
        
    return True

def crear_portada():
    print("1. Generando portada con WeasyPrint...")
    dir_original = os.getcwd()
    os.chdir("laboratorios")
    
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
    print("2. Creando contenido de programas de ordenador con LaTeX...")
    dir_original = os.getcwd()
    os.chdir("laboratorios")
    
    with open("software_utilizado.qmd", "r", encoding="utf-8") as f:
        contenido_original = f.read()
        
    partes = contenido_original.split("---")
    if len(partes) >= 3:
        contenido_sin_yaml = "---".join(partes[2:])
    else:
        contenido_sin_yaml = contenido_original
        
    yaml_latex = """---
lang: es
format:
  pdf:
    documentclass: scrreprt
    pdf-engine: pdflatex
    title-block-banner: false 
    toc: true
    toc-title: "Índice programas de ordenador"
    number-sections: false
    geometry:
      - margin=2.5cm
    fontsize: 11pt
---
"""
    
    with open("contenido_temp.qmd", "w", encoding="utf-8") as f:
        f.write(yaml_latex + "\n" + contenido_sin_yaml)
        
    try:
        subprocess.run(["quarto", "render", "contenido_temp.qmd", "--output", "contenido_temp.pdf"], env=get_conda_env(), check=True)
        if not os.path.exists("contenido_temp.pdf"):
            raise FileNotFoundError("contenido_temp.pdf no fue generado.")
        print("   [OK] Contenido de programas creado.")
    except Exception as e:
        print(f"   [ERROR] Creando contenido: {e}")
        raise e
    finally:
        os.chdir(dir_original)

def unir_pdfs(nombre_salida="SoftwareUtilizadoOptimizacionAnalisisRedes.pdf"):
    print("3. Uniendo PDFs...")
    dir_original = os.getcwd()
    os.chdir("laboratorios")
    
    portada_path = "portada_temp.pdf"
    contenido_path = "contenido_temp.pdf"
    salida_path = nombre_salida
    
    if not os.path.exists(portada_path) or not os.path.exists(contenido_path):
        raise FileNotFoundError("Faltan archivos temporales PDF para unir.")
        
    try:
        from pypdf import PdfReader, PdfWriter
        
        writer = PdfWriter()
        
        # 1. Agregar portada personalizada
        cover_reader = PdfReader(portada_path)
        writer.add_page(cover_reader.pages[0])
        
        # 2. Agregar páginas de contenido (omitiendo la página 1, que es la portada por defecto de Quarto)
        content_reader = PdfReader(contenido_path)
        print(f"   Contenido original tiene {len(content_reader.pages)} páginas.")
        
        for page_num in range(1, len(content_reader.pages)):
            writer.add_page(content_reader.pages[page_num])
            
        # 3. Guardar el PDF final
        with open(salida_path, "wb") as f_out:
            writer.write(f_out)
            
        print(f"   [OK] PDF final creado en: laboratorios/{salida_path}")
        
        # Limpieza
        temp_files = ["portada_temp.qmd", "portada_temp.pdf", "contenido_temp.qmd", "contenido_temp.pdf"]
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
                
        print("   [OK] Archivos temporales eliminados.")
    except Exception as e:
        print(f"   [ERROR] Al unir PDFs: {e}")
        raise e
    finally:
        os.chdir(dir_original)

def generar_software_completo():
    print("=== GENERACIÓN DEL LISTADO DE SOFTWARE ===")
    if not check_env():
        return
        
    try:
        crear_portada()
        crear_contenido()
        unir_pdfs()
        print("\n=== PROCESO COMPLETADO ===")
        print(f"Archivo final: laboratorios/SoftwareUtilizadoOptimizacionAnalisisRedes.pdf")
    except Exception as e:
        print(f"\n[ERROR] En el proceso: {e}")

if __name__ == "__main__":
    generar_software_completo()
