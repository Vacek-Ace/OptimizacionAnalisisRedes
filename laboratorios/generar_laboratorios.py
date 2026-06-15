import os
import subprocess
import shutil
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
        
    # Verificar directorios
    if not os.path.exists("laboratorios"):
        print("[ERROR] No se encuentra la carpeta 'laboratorios'.")
        return False
        
    # Verificar archivos necesarios
    archivos = [
        "laboratorios/portada.qmd",
        "laboratorios/portada.html",
        "laboratorios/_quarto.yml",
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
    os.chdir("laboratorios")
    
    try:
        # Renderizar portada
        subprocess.run(["quarto", "render", "portada.qmd", "--to", "pdf", "--quiet"], env=get_conda_env(), check=True)
        if not os.path.exists("portada.pdf"):
            raise FileNotFoundError("portada.pdf no fue generado.")
        print("   [OK] Portada creada.")
    except Exception as e:
        print(f"   [ERROR] Creando portada: {e}")
        raise e
    finally:
        os.chdir(dir_original)

def crear_libro():
    print("2. Renderizando libro de apuntes con Quarto...")
    
    dir_original = os.getcwd()
    os.chdir("laboratorios")
    
    try:
        # Renderizar el libro completo
        subprocess.run(["quarto", "render"], env=get_conda_env(), check=True)
        print("   [OK] Libro renderizado con exito.")
    except Exception as e:
        print(f"   [ERROR] Renderizando el libro: {e}")
        raise e
    finally:
        os.chdir(dir_original)

def unir_pdfs(nombre_salida="ApuntesOptimizacionAnalisisRedes.pdf"):
    print("3. Uniendo PDFs...")
    
    dir_original = os.getcwd()
    os.chdir("laboratorios")
    
    portada_path = "portada.pdf"
    output_dir = "laboratorios_pdf"
    
    if not os.path.exists(portada_path):
        raise FileNotFoundError("No se encontro laboratorios/portada.pdf")
        
    # Buscar el PDF del libro generado
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith(".pdf")]
    if not pdf_files:
        raise FileNotFoundError("No se encontro ningun PDF en laboratorios/laboratorios_pdf/")
        
    book_pdf_name = pdf_files[0]
    book_pdf_path = os.path.join(output_dir, book_pdf_name)
    final_pdf_path = os.path.join(output_dir, nombre_salida)
    
    try:
        from pypdf import PdfReader, PdfWriter
        
        writer = PdfWriter()
        
        # 1. Agregar portada personalizada
        cover_reader = PdfReader(portada_path)
        writer.add_page(cover_reader.pages[0])
        
        # 2. Agregar paginas del libro omitiendo la pagina 1 (portada por defecto de Quarto)
        book_reader = PdfReader(book_pdf_path)
        print(f"   Libro original tiene {len(book_reader.pages)} paginas.")
        
        for page_num in range(1, len(book_reader.pages)):
            writer.add_page(book_reader.pages[page_num])
            
        # 3. Escribir resultado final
        with open(final_pdf_path, "wb") as f_out:
            writer.write(f_out)
            
        print(f"   [OK] PDF final creado en: {final_pdf_path}")
        
        # Limpieza
        if os.path.exists(portada_path):
            os.remove(portada_path)
            
        os.remove(book_pdf_path)
        
        print("   [OK] Archivos temporales eliminados.")
    except Exception as e:
        print(f"   [ERROR] Uniendo PDFs: {e}")
        raise e
    finally:
        os.chdir(dir_original)

def generar_apuntes_completos():
    print("=== GENERACION DE APUNTES Y LABORATORIOS ===")
    if not check_env():
        return
        
    try:
        crear_portada()
        crear_libro()
        unir_pdfs()
        print("\n=== PROCESO COMPLETADO CON EXITO ===")
    except Exception as e:
        print(f"\n[ERROR] Durante el proceso: {e}")

if __name__ == "__main__":
    generar_apuntes_completos()
