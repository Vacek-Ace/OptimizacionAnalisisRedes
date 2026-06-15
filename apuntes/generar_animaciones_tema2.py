import os
import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.interpolate import pchip_interpolate
from PIL import Image

output_dir = r"C:\Users\vacek\Proyectos\OptimizacionAnalisisRedes\images"
os.makedirs(output_dir, exist_ok=True)

# Theme Colors (Cerulean style)
C_PRIMARY = '#0284c7'     # Cerulean
C_BG = '#f0f9ff'          # Light sky blue
C_TEXT = '#0f172a'        # Slate 900
C_TEXT_MUTED = '#64748b'  # Slate 500
C_ALERT = '#ef4444'       # Coral Red
C_SUCCESS = '#10b981'     # Emerald Green
C_ACCENT = '#f59e0b'      # Amber

# Target Function and Derivatives
f = lambda x: 0.25*x**4 - (13/3)*x**3 + 27*x**2 - 72*x + 1
df = lambda x: x**3 - 13*x**2 + 54*x - 72
ddf = lambda x: 3*x**2 - 26*x + 54

def fig_to_pil(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img = Image.open(buf)
    # Load image data into memory before closing the buffer
    img.load()
    buf.close()
    return img

def gen_seccion_aurea_animation():
    print("Generating Seccion Aurea animation...")
    alpha = (1 + np.sqrt(5)) / 2
    a_init, b_init = 1.0, 4.0
    a, b = 1.0, 4.0
    tol = 0.15
    n_iter = int(np.ceil((np.log(b - a) - np.log(tol)) / np.log(alpha)))
    
    frames = []
    # Save a multi-panel figure for PDF
    pdf_steps = [1, 2, 3, 4]
    fig_pdf, axes_pdf = plt.subplots(2, 2, figsize=(12, 10))
    axes_pdf = axes_pdf.flatten()
    pdf_idx = 0

    for k in range(n_iter):
        I = (b - a) / alpha
        lmbda = b - I
        mu = a + I
        
        # Create plot for the current step
        fig, ax = plt.subplots(figsize=(8, 5))
        x_vals = np.linspace(0.5, 4.5, 300)
        ax.plot(x_vals, f(x_vals), color=C_PRIMARY, lw=2.5, label=r'$f(x)$')
        
        # Shade accumulated discarded regions (hollow outlines)
        labeled_hist = False
        if a > a_init:
            ax.axvspan(a_init, a, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Descartes acumulados')
            labeled_hist = True
        if b < b_init:
            ax.axvspan(b, b_init, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Descartes acumulados' if not labeled_hist else None)
            
        # Draw lambda and mu
        ax.axvline(lmbda, color=C_TEXT_MUTED, linestyle='--', lw=1.2)
        ax.axvline(mu, color=C_TEXT_MUTED, linestyle='--', lw=1.2)
        ax.plot(lmbda, f(lmbda), 'o', color=C_ACCENT, markersize=8, label=r'$\lambda_k$')
        ax.plot(mu, f(mu), 'o', color=C_SUCCESS, markersize=8, label=r'$\mu_k$')
        
        # Highlight discarded region
        if f(lmbda) < f(mu):
            discard_a, discard_b = mu, b
            b_next = mu
            a_next = a
        else:
            discard_a, discard_b = a, lmbda
            a_next = lmbda
            b_next = b
            
        ax.axvspan(discard_a, discard_b, facecolor='none', edgecolor='#ef4444', hatch='/', linewidth=1.8, label='Descarte del paso')
        
        # Labels and Title
        ax.set_title(f"Sección Áurea - Paso {k+1}\nIntervalo: [{a:.3f}, {b:.3f}], $I_k$ = {b-a:.3f}", color=C_TEXT, fontsize=12)
        ax.set_xlabel('$x$')
        ax.set_ylabel('$f(x)$')
        ax.set_xlim(0.8, 4.2)
        ax.set_ylim(-75, -45)
        ax.legend(loc='lower left', frameon=True, facecolor='white', edgecolor='none')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add to GIF frames
        frames.append(fig_to_pil(fig))
        
        # Add to PDF multi-panel if applicable
        if (k + 1) in pdf_steps:
            ax_pdf = axes_pdf[pdf_idx]
            ax_pdf.plot(x_vals, f(x_vals), color=C_PRIMARY, lw=2)
            if a > a_init:
                ax_pdf.axvspan(a_init, a, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.0, alpha=0.6)
            if b < b_init:
                ax_pdf.axvspan(b, b_init, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.0, alpha=0.6)
            ax_pdf.axvline(lmbda, color=C_TEXT_MUTED, linestyle='--', lw=1)
            ax_pdf.axvline(mu, color=C_TEXT_MUTED, linestyle='--', lw=1)
            ax_pdf.plot(lmbda, f(lmbda), 'o', color=C_ACCENT, markersize=6)
            ax_pdf.plot(mu, f(mu), 'o', color=C_SUCCESS, markersize=6)
            ax_pdf.axvspan(discard_a, discard_b, facecolor='none', edgecolor='#ef4444', hatch='/', linewidth=1.2)
            ax_pdf.set_title(f"Paso {k+1}: [{a:.3f}, {b:.3f}]", fontsize=10)
            ax_pdf.set_xlim(0.8, 4.2)
            ax_pdf.set_ylim(-75, -45)
            ax_pdf.spines['top'].set_visible(False)
            ax_pdf.spines['right'].set_visible(False)
            pdf_idx += 1
            
        plt.close(fig)
        
        # Actualizar intervalo
        a, b = a_next, b_next
        
    # Save GIF
    gif_path = os.path.join(output_dir, "seccion_aurea.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], optimize=False, duration=1500, loop=0)
    print(f"Saved: {gif_path}")
    
    # Save PDF steps figure
    fig_pdf.suptitle("Evolución de la Búsqueda por Sección Áurea (Pasos 1 a 4)", fontsize=14, color=C_TEXT, weight='bold')
    plt.tight_layout()
    pdf_fig_path = os.path.join(output_dir, "seccion_aurea_pasos.png")
    fig_pdf.savefig(pdf_fig_path, dpi=300, transparent=True)
    plt.close(fig_pdf)
    print(f"Saved: {pdf_fig_path}")

def gen_biseccion_animation():
    print("Generating Biseccion animation...")
    a_init, b_init = 1.0, 4.0
    a, b = 1.0, 4.0
    tol = 0.15
    frames = []
    
    pdf_steps = [1, 2, 3, 4]
    fig_pdf, axes_pdf = plt.subplots(2, 2, figsize=(12, 10))
    axes_pdf = axes_pdf.flatten()
    pdf_idx = 0
    
    for k in range(10): # Max 10 steps
        c = (a + b) / 2
        df_c = df(c)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        x_vals = np.linspace(0.5, 4.5, 300)
        ax.plot(x_vals, f(x_vals), color=C_PRIMARY, lw=2.5, label=r'$f(x)$')
        
        # Shade accumulated discarded regions (hollow outlines)
        labeled_hist = False
        if a > a_init:
            ax.axvspan(a_init, a, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Descartes acumulados')
            labeled_hist = True
        if b < b_init:
            ax.axvspan(b, b_init, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Descartes acumulados' if not labeled_hist else None)
            
        # Midpoint
        ax.axvline(c, color=C_ACCENT, linestyle='--', lw=1.5)
        ax.plot(c, f(c), 'o', color=C_ACCENT, markersize=8, label=f'Punto medio $c={c:.4f}$')
        
        # Tangent line at c
        tangent_x = np.linspace(c - 0.5, c + 0.5, 50)
        tangent_y = f(c) + df_c * (tangent_x - c)
        ax.plot(tangent_x, tangent_y, color=C_ALERT, lw=2, label=f"Pendiente $f'(c)={df_c:.3f}$")
        
        # Determine discarded region
        if df_c < 0:
            discard_a, discard_b = a, c
            a_next = c
            b_next = b
        else:
            discard_a, discard_b = c, b
            a_next = a
            b_next = c
            
        ax.axvspan(discard_a, discard_b, facecolor='none', edgecolor='#ef4444', hatch='\\', linewidth=1.8, label='Descarte del paso')
        
        ax.set_title(f"Bisección (Bolzano) - Paso {k+1}\nIntervalo: [{a:.4f}, {b:.4f}], $f'(c)$ = {df_c:.4f}", color=C_TEXT, fontsize=12)
        ax.set_xlabel('$x$')
        ax.set_ylabel('$f(x)$')
        ax.set_xlim(0.8, 4.2)
        ax.set_ylim(-75, -45)
        ax.legend(loc='lower left', frameon=True, facecolor='white', edgecolor='none')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        frames.append(fig_to_pil(fig))
        
        if (k + 1) in pdf_steps:
            ax_pdf = axes_pdf[pdf_idx]
            ax_pdf.plot(x_vals, f(x_vals), color=C_PRIMARY, lw=2)
            if a > a_init:
                ax_pdf.axvspan(a_init, a, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.0, alpha=0.6)
            if b < b_init:
                ax_pdf.axvspan(b, b_init, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.0, alpha=0.6)
            ax_pdf.axvline(c, color=C_ACCENT, linestyle='--', lw=1)
            ax_pdf.plot(c, f(c), 'o', color=C_ACCENT, markersize=6)
            ax_pdf.plot(tangent_x, tangent_y, color=C_ALERT, lw=1.5)
            ax_pdf.axvspan(discard_a, discard_b, facecolor='none', edgecolor='#ef4444', hatch='\\', linewidth=1.2)
            ax_pdf.set_title(f"Paso {k+1}: [{a:.3f}, {b:.3f}], $f'(c)$={df_c:.3f}", fontsize=10)
            ax_pdf.set_xlim(0.8, 4.2)
            ax_pdf.set_ylim(-75, -45)
            ax_pdf.spines['top'].set_visible(False)
            ax_pdf.spines['right'].set_visible(False)
            pdf_idx += 1
            
        plt.close(fig)
        
        # Actualizar intervalo
        a, b = a_next, b_next
        if (b - a) < tol:
            break
            
    # Save GIF
    gif_path = os.path.join(output_dir, "biseccion.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], optimize=False, duration=1500, loop=0)
    print(f"Saved: {gif_path}")
    
    # Save PDF steps figure
    fig_pdf.suptitle("Evolución de la Búsqueda por Bisección (Pasos 1 a 4)", fontsize=14, color=C_TEXT, weight='bold')
    plt.tight_layout()
    pdf_fig_path = os.path.join(output_dir, "biseccion_pasos.png")
    fig_pdf.savefig(pdf_fig_path, dpi=300, transparent=True)
    plt.close(fig_pdf)
    print(f"Saved: {pdf_fig_path}")

def gen_newton_1d_animation():
    print("Generating Newton 1D animation...")
    x = 1.0
    tol = 1e-5
    frames = []
    
    pdf_steps = [1, 2, 3, 4]
    fig_pdf, axes_pdf = plt.subplots(2, 2, figsize=(12, 10))
    axes_pdf = axes_pdf.flatten()
    pdf_idx = 0
    
    for k in range(5):
        val_f = f(x)
        val_df = df(x)
        val_ddf = ddf(x)
        
        x_new = x - val_df / val_ddf
        
        fig, ax = plt.subplots(figsize=(8, 5))
        x_vals = np.linspace(0.5, 4.5, 300)
        ax.plot(x_vals, f(x_vals), color=C_PRIMARY, lw=2.5, label=r'$f(x)$')
        
        # Parábola de aproximación de Taylor en x_k
        # q(z) = f(x_k) + f'(x_k)(z-x_k) + 0.5 * f''(x_k)(z-x_k)^2
        q = lambda z: val_f + val_df * (z - x) + 0.5 * val_ddf * (z - x)**2
        ax.plot(x_vals, q(x_vals), color='#a855f7', lw=1.8, linestyle='--', label=r'Aproximación cuadrática $q(x)$')
        
        # Highlight current point
        ax.plot(x, val_f, 'o', color=C_ALERT, markersize=8)
        ax.text(x, val_f + 3, f'$x_{k}={x:.3f}$', ha='center', va='bottom', color=C_ALERT, fontweight='bold')
        
        # Highlight jump to next point
        ax.plot(x_new, q(x_new), 'x', color=C_SUCCESS, markersize=10, mew=2, label=f'Siguiente iteración $x_{{k+1}}={x_new:.3f}$')
        ax.annotate('', xy=(x_new, q(x_new)), xytext=(x, val_f),
                    arrowprops=dict(arrowstyle="->", color='#8b5cf6', lw=1.5, connectionstyle="arc3,rad=-0.1"))
        
        ax.set_title(f"Método de Newton 1D - Paso {k+1}\n$x_{k}$ = {x:.4f} $\\rightarrow$ $x_{{k+1}}$ = {x_new:.4f}", color=C_TEXT, fontsize=12)
        ax.set_xlabel('$x$')
        ax.set_ylabel('$f(x)$')
        ax.set_xlim(0.8, 4.2)
        ax.set_ylim(-75, -15)
        ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='none')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        frames.append(fig_to_pil(fig))
        
        if (k + 1) in pdf_steps:
            ax_pdf = axes_pdf[pdf_idx]
            ax_pdf.plot(x_vals, f(x_vals), color=C_PRIMARY, lw=2)
            ax_pdf.plot(x_vals, q(x_vals), color='#a855f7', lw=1.2, linestyle='--')
            ax_pdf.plot(x, val_f, 'o', color=C_ALERT, markersize=6)
            ax_pdf.plot(x_new, q(x_new), 'x', color=C_SUCCESS, markersize=6, mew=1.5)
            ax_pdf.annotate('', xy=(x_new, q(x_new)), xytext=(x, val_f),
                        arrowprops=dict(arrowstyle="->", color='#8b5cf6', lw=1))
            ax_pdf.set_title(f"Paso {k+1}: $x_{k}={x:.3f} \\rightarrow {x_new:.3f}$", fontsize=10)
            ax_pdf.set_xlim(0.8, 4.2)
            ax_pdf.set_ylim(-75, -15)
            ax_pdf.spines['top'].set_visible(False)
            ax_pdf.spines['right'].set_visible(False)
            pdf_idx += 1
            
        plt.close(fig)
        
        if abs(x_new - x) < tol:
            break
        x = x_new
        
    # Save GIF
    gif_path = os.path.join(output_dir, "newton_1d.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], optimize=False, duration=1500, loop=0)
    print(f"Saved: {gif_path}")
    
    # Save PDF steps figure
    fig_pdf.suptitle("Evolución del Método de Newton 1D (Pasos 1 a 4)", fontsize=14, color=C_TEXT, weight='bold')
    plt.tight_layout()
    pdf_fig_path = os.path.join(output_dir, "newton_1d_pasos.png")
    fig_pdf.savefig(pdf_fig_path, dpi=300, transparent=True)
    plt.close(fig_pdf)
    print(f"Saved: {pdf_fig_path}")

def gen_tipos_optimos():
    print("Generating tipos_optimos.png...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 1. Convex Case (Left)
    x1 = np.linspace(0.5, 4.5, 200)
    y1 = (x1 - 2.5)**2 + 1.0
    ax1.plot(x1, y1, color=C_PRIMARY, lw=3)
    ax1.plot(2.5, 1.0, 'o', color=C_SUCCESS, markersize=10, label='Mínimo global (estricto)')
    ax1.set_title("Caso Convexo (Unimodal)", color=C_TEXT, fontsize=12, fontweight='bold')
    ax1.set_xlabel('$x$', fontsize=10)
    ax1.set_ylabel('$f(x)$', fontsize=10)
    ax1.set_xlim(0.3, 4.7)
    ax1.set_ylim(0.5, 6.0)
    ax1.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='none')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # 2. Non-Convex Case (Right)
    # Define control points for Pchip
    ctrl_x = np.array([1.0, 2.5, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    ctrl_y = np.array([4.0, 0.8, 2.5, 1.5, 2.2, 2.2, 2.3, 4.0])
    x2 = np.linspace(1.0, 9.0, 300)
    y2 = pchip_interpolate(ctrl_x, ctrl_y, x2)
    
    ax2.plot(x2, y2, color=C_PRIMARY, lw=3)
    # Annotate critical points
    # Global Min at ~2.5
    ax2.plot(2.5, 0.8, 'o', color=C_SUCCESS, markersize=10, label='Mínimo global (estricto)')
    # Local Min at ~5.0
    ax2.plot(5.0, 1.5, 'o', color='#06b6d4', markersize=8, label='Mínimo local (estricto)')
    # Flat Local Min between 6.0 and 7.0
    flat_x = np.linspace(6.0, 7.0, 50)
    flat_y = np.full_like(flat_x, 2.2)
    ax2.plot(flat_x, flat_y, color=C_ALERT, lw=4, label='Mínimos locales (no estrictos)')
    
    ax2.set_title("Caso No Convexo", color=C_TEXT, fontsize=12, fontweight='bold')
    ax2.set_xlabel('$x$', fontsize=10)
    ax2.set_ylabel('$f(x)$', fontsize=10)
    ax2.set_xlim(0.8, 9.2)
    ax2.set_ylim(0.5, 4.5)
    ax2.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='none')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "tipos_optimos.png"), dpi=300, transparent=True)
    plt.close(fig)
    print("Saved tipos_optimos.png")

def gen_busqueda_uniforme_concepto():
    print("Generating busqueda_uniforme_concepto.png and busqueda_uniforme.gif...")
    
    # We will generate frames
    frames = []
    
    # Define function
    f_unimodal = lambda x: (x - 2.7)**2 + 0.8
    x_vals = np.linspace(0.5, 5.5, 300)
    a, b = 0.5, 5.5
    grid_points = np.linspace(a, b, 11) # 11 points: 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5
    
    # We create the 5 frames
    for step in range(5):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(x_vals, f_unimodal(x_vals), color=C_PRIMARY, lw=3, label=r'$f(x)$')
        
        # Frame 0: Initial interval
        if step == 0:
            ax.axvspan(a, b, color=C_BG, alpha=0.5, label='Intervalo inicial $[a, b]$')
            ax.text(a, -0.15, r'$a$', ha='center', va='top', fontsize=9, color=C_TEXT)
            ax.text(b, -0.15, r'$b$', ha='center', va='top', fontsize=9, color=C_TEXT)
            
        # Frame 1: Grid points & evaluations
        elif step == 1:
            ax.axvspan(a, b, color=C_BG, alpha=0.5, label='Intervalo inicial $[a, b]$')
            for i, gp in enumerate(grid_points):
                ax.vlines(gp, 0, f_unimodal(gp), colors=C_TEXT_MUTED, linestyles=':', alpha=0.6)
                # Mark evaluations
                ax.plot(gp, f_unimodal(gp), 'o', color=C_TEXT_MUTED, markersize=5)
                # Label
                label = r'$a$' if i == 0 else (r'$b$' if i == 10 else f'$a_{i}$')
                ax.text(gp, -0.15, label, ha='center', va='top', fontsize=9, color=C_TEXT)
                
        # Frame 2: Minimum point
        elif step == 2:
            ax.axvspan(a, b, color=C_BG, alpha=0.5, label='Intervalo inicial $[a, b]$')
            for i, gp in enumerate(grid_points):
                ax.vlines(gp, 0, f_unimodal(gp), colors=C_TEXT_MUTED, linestyles=':', alpha=0.6)
                if i == 4:
                    ax.plot(gp, f_unimodal(gp), 'o', color=C_ALERT, markersize=8, label=r'$a_{k^*}$ (Mínimo evaluado)')
                else:
                    ax.plot(gp, f_unimodal(gp), 'o', color=C_TEXT_MUTED, markersize=5)
                label = r'$a$' if i == 0 else (r'$b$' if i == 10 else f'$a_{i}$')
                ax.text(gp, -0.15, label, ha='center', va='top', fontsize=9, color=C_TEXT)
                
        # Frame 3: Discarded regions
        elif step == 3:
            # Show original interval
            ax.axvspan(a, b, color=C_BG, alpha=0.5)
            # Show previous/current discards: [a, a_3] and [a_5, b]
            ax.axvspan(a, 2.0, color='#ef4444', alpha=0.25, hatch='/')
            ax.axvspan(3.0, b, color='#ef4444', alpha=0.25, hatch='/', label='Regiones descartadas')
            for i, gp in enumerate(grid_points):
                ax.vlines(gp, 0, f_unimodal(gp), colors=C_TEXT_MUTED, linestyles=':', alpha=0.6)
                if i == 4:
                    ax.plot(gp, f_unimodal(gp), 'o', color=C_ALERT, markersize=8, label=r'$a_{k^*}$')
                else:
                    ax.plot(gp, f_unimodal(gp), 'o', color=C_TEXT_MUTED, markersize=5)
                label = r'$a$' if i == 0 else (r'$b$' if i == 10 else f'$a_{i}$')
                ax.text(gp, -0.15, label, ha='center', va='top', fontsize=9, color=C_TEXT)
                
        # Frame 4: Final active interval
        elif step == 4:
            # Shaded discarded regions (hatch)
            ax.axvspan(a, 2.0, color='#ef4444', alpha=0.25, hatch='/')
            ax.axvspan(3.0, b, color='#ef4444', alpha=0.25, hatch='/', label='Regiones descartadas')
            # Highlight new active interval
            ax.axvspan(2.0, 3.0, color=C_BG, alpha=0.5, label='Nuevo intervalo $[a_{k^*-1}, a_{k^*+1}]$')
            ax.vlines([2.0, 3.0], 0, f_unimodal(np.array([2.0, 3.0])), colors=C_SUCCESS, linestyles='--', lw=1.5)
            
            for i, gp in enumerate(grid_points):
                ax.vlines(gp, 0, f_unimodal(gp), colors=C_TEXT_MUTED, linestyles=':', alpha=0.6)
                if i == 4:
                    ax.plot(gp, f_unimodal(gp), 'o', color=C_ALERT, markersize=8, label=r'$a_{k^*}$')
                else:
                    ax.plot(gp, f_unimodal(gp), 'o', color=C_TEXT_MUTED, markersize=5)
                label = r'$a$' if i == 0 else (r'$b$' if i == 10 else f'$a_{i}$')
                ax.text(gp, -0.15, label, ha='center', va='top', fontsize=9, color=C_TEXT)

        # Settings
        ax.set_title(f"Búsqueda Uniforme (Rejilla) - Paso {step}", color=C_TEXT, fontsize=12, fontweight='bold')
        ax.set_xlabel('$x$', labelpad=15)
        ax.set_ylabel('$f(x)$')
        ax.set_xlim(0.3, 5.7)
        ax.set_ylim(0, 9.0)
        ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='none')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        img = fig_to_pil(fig)
        frames.append(img)
        
        # Save step 4 as the static image
        if step == 4:
            ax.set_title("Búsqueda Uniforme (Rejilla)", color=C_TEXT, fontsize=12, fontweight='bold')
            plt.tight_layout()
            fig.savefig(os.path.join(output_dir, "busqueda_uniforme_concepto.png"), dpi=300, transparent=True)
            print("Saved busqueda_uniforme_concepto.png")
            
        plt.close(fig)
        
    # Save GIF
    gif_path = os.path.join(output_dir, "busqueda_uniforme.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], optimize=False, duration=1800, loop=0)
    print(f"Saved: {gif_path}")

def gen_busqueda_dicotomica_insuficiente():
    print("Generating busqueda_dicotomica_insuficiente.png...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Subplot 1: Minimum on the left
    x1 = np.linspace(1.0, 5.0, 200)
    f1 = lambda x: (x - 2.0)**2 + 1.0
    ax1.plot(x1, f1(x1), color=C_PRIMARY, lw=3)
    ax1.vlines(3.0, 0, f1(3.0), colors=C_ALERT, linestyles='--')
    ax1.plot(3.0, f1(3.0), 'o', color=C_ALERT, markersize=8)
    # Boundaries
    ax1.vlines([1.0, 5.0], 0, [f1(1.0), f1(5.0)], colors=C_TEXT_MUTED, linestyles=':')
    ax1.text(1.0, -0.2, '$a$', ha='center', va='top', fontsize=10)
    ax1.text(5.0, -0.2, '$b$', ha='center', va='top', fontsize=10)
    ax1.text(3.0, -0.2, '$c$', ha='center', va='top', fontsize=10, color=C_ALERT, fontweight='bold')
    ax1.set_title("Caso 1: Mínimo a la izquierda de $c$", color=C_TEXT, fontsize=11)
    ax1.set_xlabel('$x$')
    ax1.set_ylabel('$f(x)$')
    ax1.set_xlim(0.8, 5.2)
    ax1.set_ylim(0, 6.0)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Subplot 2: Minimum on the right
    x2 = np.linspace(1.0, 5.0, 200)
    f2 = lambda x: (x - 4.0)**2 + 1.0
    ax2.plot(x2, f2(x2), color=C_PRIMARY, lw=3)
    ax2.vlines(3.0, 0, f2(3.0), colors=C_ALERT, linestyles='--')
    ax2.plot(3.0, f2(3.0), 'o', color=C_ALERT, markersize=8)
    # Boundaries
    ax2.vlines([1.0, 5.0], 0, [f2(1.0), f2(5.0)], colors=C_TEXT_MUTED, linestyles=':')
    ax2.text(1.0, -0.2, '$a$', ha='center', va='top', fontsize=10)
    ax2.text(5.0, -0.2, '$b$', ha='center', va='top', fontsize=10)
    ax2.text(3.0, -0.2, '$c$', ha='center', va='top', fontsize=10, color=C_ALERT, fontweight='bold')
    ax2.set_title("Caso 2: Mínimo a la derecha de $c$", color=C_TEXT, fontsize=11)
    ax2.set_xlabel('$x$')
    ax2.set_ylabel('$f(x)$')
    ax2.set_xlim(0.8, 5.2)
    ax2.set_ylim(0, 6.0)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    fig.suptitle("Un solo punto medio $c$ no es suficiente para decidir el descarte\n(ambas funciones tienen idéntico valor $f(c)$)", color=C_TEXT, fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "busqueda_dicotomica_insuficiente.png"), dpi=300, transparent=True)
    plt.close(fig)
    print("Saved busqueda_dicotomica_insuficiente.png")

def gen_busqueda_dicotomica_concepto():
    print("Generating busqueda_dicotomica_concepto.png...")
    fig, ax = plt.subplots(figsize=(8, 5))
    
    x_vals = np.linspace(1.0, 5.0, 300)
    f_unimodal = lambda x: (x - 2.3)**2 + 1.0
    ax.plot(x_vals, f_unimodal(x_vals), color=C_PRIMARY, lw=3, label=r'$f(x)$')
    
    # Points
    a, b = 1.0, 5.0
    c = 3.0
    lmbda = c - 0.3
    mu = c + 0.3
    
    ax.vlines([a, b], 0, [f_unimodal(a), f_unimodal(b)], colors=C_TEXT_MUTED, linestyles=':')
    ax.vlines([lmbda, mu], 0, [f_unimodal(lmbda), f_unimodal(mu)], colors=[C_ACCENT, C_SUCCESS], linestyles='--')
    ax.plot(lmbda, f_unimodal(lmbda), 'o', color=C_ACCENT, markersize=8, label=r'$\lambda_k = c - \delta$')
    ax.plot(mu, f_unimodal(mu), 'o', color=C_SUCCESS, markersize=8, label=r'$\mu_k = c + \delta$')
    
    # Shading discarded region: since f(lambda) < f(mu), we discard [mu, b]
    ax.axvspan(mu, b, color='#ef4444', alpha=0.2, hatch='//', label='Región descartada')
    
    ax.text(a, -0.15, '$a_k$', ha='center', va='top', fontsize=10)
    ax.text(b, -0.15, '$b_k$', ha='center', va='top', fontsize=10)
    ax.text(lmbda, -0.15, r'$\lambda_k$', ha='center', va='top', fontsize=10, color=C_ACCENT, fontweight='bold')
    ax.text(mu, -0.15, r'$\mu_k$', ha='center', va='top', fontsize=10, color=C_SUCCESS, fontweight='bold')
    ax.text(c, -0.15, r'$c$', ha='center', va='top', fontsize=10)
    
    ax.set_title("Búsqueda Dicotómica: Descarte de Intervalo ($f(\lambda_k) < f(\mu_k)$)", color=C_TEXT, fontsize=12, fontweight='bold')
    ax.set_xlabel('$x$', labelpad=15)
    ax.set_ylabel('$f(x)$')
    ax.set_xlim(0.8, 5.2)
    ax.set_ylim(0, 10.0)
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='none')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "busqueda_dicotomica_concepto.png"), dpi=300, transparent=True)
    plt.close(fig)
    print("Saved busqueda_dicotomica_concepto.png")

def gen_dicotomica_trace_animation():
    print("Generating Búsqueda Dicotómica animation (dicotomica.gif)...")
    a_init, b_init = 1.0, 4.0
    a, b = 1.0, 4.0
    tol = 0.15
    delta = 0.02
    
    frames = []
    pdf_steps = [1, 2, 3, 4]
    fig_pdf, axes_pdf = plt.subplots(2, 2, figsize=(12, 10))
    axes_pdf = axes_pdf.flatten()
    pdf_idx = 0
    
    for k in range(10):
        c = (a + b) / 2
        lmbda = c - delta
        mu = c + delta
        
        f_lmbda = f(lmbda)
        f_mu = f(mu)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        x_vals = np.linspace(0.5, 4.5, 300)
        ax.plot(x_vals, f(x_vals), color=C_PRIMARY, lw=2.5, label=r'$f(x)$')
        
        # Shade accumulated discarded regions (hollow outlines)
        labeled_hist = False
        if a > a_init:
            ax.axvspan(a_init, a, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Descartes acumulados')
            labeled_hist = True
        if b < b_init:
            ax.axvspan(b, b_init, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Descartes acumulados' if not labeled_hist else None)
            
        # Draw lambda and mu
        ax.axvline(lmbda, color=C_ACCENT, linestyle='--', lw=1.2)
        ax.axvline(mu, color=C_SUCCESS, linestyle='--', lw=1.2)
        ax.plot(lmbda, f_lmbda, 'o', color=C_ACCENT, markersize=8, label=r'$\lambda_k$')
        ax.plot(mu, f_mu, 'o', color=C_SUCCESS, markersize=8, label=r'$\mu_k$')
        
        # Determine discarded region
        if f_lmbda < f_mu:
            discard_a, discard_b = mu, b
            a_next = a
            b_next = mu
        else:
            discard_a, discard_b = a, lmbda
            a_next = lmbda
            b_next = b
            
        ax.axvspan(discard_a, discard_b, facecolor='none', edgecolor='#ef4444', hatch='/', linewidth=1.8, label='Descarte del paso')
        
        ax.set_title(f"Búsqueda Dicotómica - Paso {k+1}\nIntervalo: [{a:.3f}, {b:.3f}], Amplitud = {b-a:.3f}", color=C_TEXT, fontsize=12)
        ax.set_xlabel('$x$')
        ax.set_ylabel('$f(x)$')
        ax.set_xlim(0.8, 4.2)
        ax.set_ylim(-75, -45)
        ax.legend(loc='lower left', frameon=True, facecolor='white', edgecolor='none')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        frames.append(fig_to_pil(fig))
        
        if (k + 1) in pdf_steps:
            ax_pdf = axes_pdf[pdf_idx]
            ax_pdf.plot(x_vals, f(x_vals), color=C_PRIMARY, lw=2)
            if a > a_init:
                ax_pdf.axvspan(a_init, a, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.0, alpha=0.6)
            if b < b_init:
                ax_pdf.axvspan(b, b_init, facecolor='none', edgecolor='#ef4444', linestyle='--', linewidth=1.0, alpha=0.6)
            ax_pdf.axvline(lmbda, color=C_ACCENT, linestyle='--', lw=1)
            ax_pdf.axvline(mu, color=C_SUCCESS, linestyle='--', lw=1)
            ax_pdf.plot(lmbda, f_lmbda, 'o', color=C_ACCENT, markersize=6)
            ax_pdf.plot(mu, f_mu, 'o', color=C_SUCCESS, markersize=6)
            ax_pdf.axvspan(discard_a, discard_b, facecolor='none', edgecolor='#ef4444', hatch='/', linewidth=1.2)
            ax_pdf.set_title(f"Paso {k+1}: [{a:.3f}, {b:.3f}]", fontsize=10)
            ax_pdf.set_xlim(0.8, 4.2)
            ax_pdf.set_ylim(-75, -45)
            ax_pdf.spines['top'].set_visible(False)
            ax_pdf.spines['right'].set_visible(False)
            pdf_idx += 1
            
        plt.close(fig)
        
        # Update interval
        a, b = a_next, b_next
        if (b - a) < tol:
            break
            
    # Save GIF
    gif_path = os.path.join(output_dir, "dicotomica.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], optimize=False, duration=1500, loop=0)
    print(f"Saved: {gif_path}")
    
    # Save PDF steps figure
    fig_pdf.suptitle("Evolución de la Búsqueda Dicotómica (Pasos 1 a 4)", fontsize=14, color=C_TEXT, weight='bold')
    plt.tight_layout()
    pdf_fig_path = os.path.join(output_dir, "dicotomica_pasos.png")
    fig_pdf.savefig(pdf_fig_path, dpi=300, transparent=True)
    plt.close(fig_pdf)
    print(f"Saved: {pdf_fig_path}")

if __name__ == '__main__':
    print("Generating animated GIFs and static step-by-step figures...")
    gen_seccion_aurea_animation()
    gen_biseccion_animation()
    gen_newton_1d_animation()
    gen_tipos_optimos()
    gen_busqueda_uniforme_concepto()
    gen_busqueda_dicotomica_insuficiente()
    gen_busqueda_dicotomica_concepto()
    gen_dicotomica_trace_animation()
    print("All animations generated successfully.")
