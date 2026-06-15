import os
import io
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
from PIL import Image

output_dir = r"C:\Users\vacek\Proyectos\OptimizacionAnalisisRedes\images"
os.makedirs(output_dir, exist_ok=True)

C_PRIMARY    = '#0284c7'
C_BG         = '#f0f9ff'
C_TEXT       = '#0f172a'
C_TEXT_MUTED = '#64748b'
C_ALERT      = '#ef4444'
C_SUCCESS    = '#10b981'
C_ACCENT     = '#f59e0b'
C_PURPLE     = '#7c3aed'


def fig_to_pil(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img = Image.open(buf)
    img.load()
    buf.close()
    return img


def gen_coord_ciclicas_ej1_animation():
    print("Generating coordenadas_ciclicas_ej1.gif ...")
    x_grid = np.linspace(-0.5, 4.5, 300)
    y_grid = np.linspace(-0.5, 4.5, 300)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z = (X - 2)**2 + (Y - 1)**2
    levels = [0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0]

    traj_x = [0.0, 2.0, 2.0]
    traj_y = [0.0, 0.0, 1.0]
    labels  = [r'$x_0=(0,0)$', r'$x_1=(2,0)$', r'$x_2=x^*=(2,1)$']
    offsets = [(0, -0.35), (0, -0.35), (0, 0.32)]
    lcols   = [C_TEXT, C_TEXT, C_SUCCESS]
    step_titles = [
        "Inicio: $x_0=(0,0)^T$,  $f(x_0)=5.0$",
        "Paso 1 (min en $x$): $x_1=(2,0)^T$,  $f=1.0$",
        "Paso 2 (min en $y$): $x_2=(2,1)^T=x^*$,  $f=0$",
    ]

    frames = []
    fig_pdf, axes_pdf = plt.subplots(1, 3, figsize=(15, 5))

    for k in range(3):
        fig, ax = plt.subplots(figsize=(6, 6))
        ct = ax.contour(X, Y, Z, levels=levels, colors='black', alpha=0.4, linewidths=1)
        ax.clabel(ct, inline=True, fontsize=7, fmt='%.1f')
        for i in range(k + 1):
            c = C_SUCCESS if i == 2 else C_ALERT
            m = '*' if i == 2 else 'o'
            s = 13 if i == 2 else 8
            ax.plot(traj_x[i], traj_y[i], m, color=c, markersize=s, zorder=10)
            ax.text(traj_x[i]+offsets[i][0], traj_y[i]+offsets[i][1], labels[i],
                    fontsize=9, ha='center', color=lcols[i],
                    fontweight='bold' if i == 2 else 'normal')
        for i in range(k):
            ax.annotate('', xy=(traj_x[i+1], traj_y[i+1]), xytext=(traj_x[i], traj_y[i]),
                        arrowprops=dict(arrowstyle='-|>', color=C_ALERT, lw=2.5, mutation_scale=15))
        ax.set_title(f"Coordenadas ciclicas\n{step_titles[k]}", color=C_TEXT, fontsize=10, pad=10)
        ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 4.5)
        ax.set_xlabel('$x$', fontsize=11); ax.set_ylabel('$y$', fontsize=11)
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        ax.set_aspect('equal')
        plt.tight_layout()
        frames.append(fig_to_pil(fig))

        ap = axes_pdf[k]
        ap.contour(X, Y, Z, levels=levels, colors='black', alpha=0.4, linewidths=0.8)
        for i in range(k + 1):
            c = C_SUCCESS if i == 2 else C_ALERT
            m = '*' if i == 2 else 'o'
            ap.plot(traj_x[i], traj_y[i], m, color=c, markersize=8 if i == 2 else 5, zorder=10)
            ap.text(traj_x[i]+offsets[i][0], traj_y[i]+offsets[i][1], labels[i], fontsize=7, ha='center')
        for i in range(k):
            ap.annotate('', xy=(traj_x[i+1], traj_y[i+1]), xytext=(traj_x[i], traj_y[i]),
                        arrowprops=dict(arrowstyle='-|>', color=C_ALERT, lw=1.5, mutation_scale=10))
        ap.set_xlim(-0.5, 4.5); ap.set_ylim(-0.5, 4.5)
        ap.set_title(f"Paso {k}", fontsize=9); ap.set_aspect('equal')
        ap.spines['top'].set_visible(False); ap.spines['right'].set_visible(False)
        plt.close(fig)

    gif_path = os.path.join(output_dir, "coordenadas_ciclicas_ej1.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:],
                   optimize=False, duration=1800, loop=0)
    print(f"  Saved: {gif_path}")
    fig_pdf.suptitle(r"Descenso por coordenadas: $f(x,y)=(x-2)^2+(y-1)^2$",
                     fontsize=12, color=C_TEXT, fontweight='bold')
    plt.tight_layout()
    pp = os.path.join(output_dir, "coordenadas_ciclicas_ej1_pasos.png")
    fig_pdf.savefig(pp, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig_pdf)
    print(f"  Saved: {pp}")


def gen_coord_ciclicas_ej2_animation():
    print("Generating coordenadas_ciclicas_ej2.gif ...")
    x_grid = np.linspace(-1, 5, 300)
    y_grid = np.linspace(-5, 1.5, 300)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z = 8*X**2 + 3*X*Y + 7*Y**2 - 25*X + 31*Y - 29
    levels = [-50, -40, -20, 0, 50, 100, 200, 400]

    traj_x = [0.0, 25/16, 25/16, 7313/3584, 2.060]
    traj_y = [0.0, 0.0, -571/224, -571/224, -2.656]
    labs   = [r'$x_0$', r'$x_1$', r'$x_2$', r'$x_3$', r'$x^*$']
    offsets = [(0.12, 0.25), (0.18, 0.25), (-0.30, -0.30), (0.22, 0.22), (0.28, -0.30)]
    lcols   = [C_TEXT]*4 + [C_SUCCESS]
    step_titles = [
        "Inicio: $x_0=(0,0)$",
        "Paso 1 (min en $x$): $x_1=(1.56,0)$",
        "Paso 2 (min en $y$): $x_2=(1.56,-2.55)$",
        "Paso 3 (min en $x$): $x_3=(2.04,-2.55)$",
        "Convergencia al optimo $x^*=(2.06,-2.66)$",
    ]

    frames = []
    n_pdf = len(traj_x)
    fig_pdf, axes_pdf = plt.subplots(1, n_pdf, figsize=(5*n_pdf, 5))

    for k in range(len(traj_x)):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.contour(X, Y, Z, levels=levels, colors='black', alpha=0.4, linewidths=1)
        for i in range(k + 1):
            c = C_SUCCESS if i == len(traj_x)-1 else C_ALERT
            m = '*' if i == len(traj_x)-1 else 'o'
            s = 13 if m == '*' else 7
            ax.plot(traj_x[i], traj_y[i], m, color=c, markersize=s, zorder=10)
            ax.text(traj_x[i]+offsets[i][0], traj_y[i]+offsets[i][1], labs[i], fontsize=9, color=lcols[i],
                    fontweight='bold' if i == len(traj_x)-1 else 'normal')
        for i in range(k):
            ax.annotate('', xy=(traj_x[i+1], traj_y[i+1]), xytext=(traj_x[i], traj_y[i]),
                        arrowprops=dict(arrowstyle='-|>', color=C_ALERT, lw=2.5, mutation_scale=15))
        ax.set_title(f"Coordenadas ciclicas\n{step_titles[k]}", color=C_TEXT, fontsize=9, pad=10)
        ax.set_xlim(-1, 5); ax.set_ylim(-5, 1.5)
        ax.set_xlabel('$x$', fontsize=11); ax.set_ylabel('$y$', fontsize=11)
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        ax.set_aspect('equal')
        plt.tight_layout()
        frames.append(fig_to_pil(fig))

        ap = axes_pdf[k]
        ap.contour(X, Y, Z, levels=levels, colors='black', alpha=0.4, linewidths=0.8)
        for i in range(k + 1):
            c = C_SUCCESS if i == len(traj_x)-1 else C_ALERT
            m = '*' if i == len(traj_x)-1 else 'o'
            ap.plot(traj_x[i], traj_y[i], m, color=c, markersize=8 if m == '*' else 5, zorder=10)
            ap.text(traj_x[i]+offsets[i][0], traj_y[i]+offsets[i][1], labs[i], fontsize=7)
        for i in range(k):
            ap.annotate('', xy=(traj_x[i+1], traj_y[i+1]), xytext=(traj_x[i], traj_y[i]),
                        arrowprops=dict(arrowstyle='-|>', color=C_ALERT, lw=1.5, mutation_scale=10))
        ap.set_xlim(-1, 5); ap.set_ylim(-5, 1.5)
        ap.set_title(f"Paso {k}", fontsize=8); ap.set_aspect('equal')
        ap.spines['top'].set_visible(False); ap.spines['right'].set_visible(False)
        plt.close(fig)

    gif_path = os.path.join(output_dir, "coordenadas_ciclicas_ej2.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:],
                   optimize=False, duration=2000, loop=0)
    print(f"  Saved: {gif_path}")
    fig_pdf.suptitle(r"Coordenadas ciclicas: $f(x,y)=8x^2+3xy+7y^2-25x+31y-29$",
                     fontsize=12, color=C_TEXT, fontweight='bold')
    plt.tight_layout()
    pp = os.path.join(output_dir, "coordenadas_ciclicas_ej2_pasos.png")
    fig_pdf.savefig(pp, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig_pdf)
    print(f"  Saved: {pp}")


def gen_steepest_descent_animation():
    print("Generating steepest_descent.gif ...")
    f  = lambda xy: 8*xy[0]**2 + 3*xy[0]*xy[1] + 7*xy[1]**2 - 25*xy[0] + 31*xy[1] - 29
    gf = lambda xy: np.array([16*xy[0] + 3*xy[1] - 25, 3*xy[0] + 14*xy[1] + 31])

    x_grid = np.linspace(-3.5, 5, 300)
    y_grid = np.linspace(-5, 4.5, 300)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z = 8*X**2 + 3*X*Y + 7*Y**2 - 25*X + 31*Y - 29
    levels = [-50, -40, -20, 0, 50, 100, 200, 400]

    # Solo 2 iteraciones, consistentes con el ejemplo del texto
    # x0=(0,0) -> x1=(2.109,-2.615) -> x2~x*=(2.060,-2.656)
    x = np.array([0.0, 0.0])
    traj, grads, dirs = [x.copy()], [], []
    for _ in range(2):
        g = gf(x); d = -g
        grads.append(g.copy()); dirs.append(d.copy())
        alpha = minimize_scalar(lambda a: f(x + a*d), bounds=(0, 10), method='bounded').x
        x = x + alpha * d
        traj.append(x.copy())

    def fmt_pt(pt):
        """Formato limpio sin np.float64: (x, y)"""
        return f"({float(pt[0]):.3f}, {float(pt[1]):.3f})"

    frames = []
    n_pdf = len(traj)   # 3 paneles
    fig_pdf, axes_pdf = plt.subplots(1, n_pdf, figsize=(4*n_pdf, 5))

    for k in range(len(traj)):
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.contour(X, Y, Z, levels=levels, colors='black', alpha=0.4, linewidths=1)

        # Puntos visitados
        for i in range(k + 1):
            is_last = (i == len(traj)-1) and (k == len(traj)-1)
            c = C_SUCCESS if is_last else C_ALERT
            m = '*' if is_last else 'o'
            ax.plot(traj[i][0], traj[i][1], m, color=c, markersize=13 if m == '*' else 7, zorder=10)
            lbl = f'$x_{i}$' + (r'$\approx x^*$' if is_last else '')
            lbl_color = C_SUCCESS if is_last else C_TEXT
            ax.text(traj[i][0]+0.15, traj[i][1]+0.22, lbl, fontsize=9, color=lbl_color)

        # Flechas de trayectoria
        for i in range(k):
            ax.annotate('', xy=traj[i+1], xytext=traj[i],
                        arrowprops=dict(arrowstyle='-|>', color=C_ALERT, lw=2, mutation_scale=14))

        # Vectores en el punto actual
        if k < len(grads):
            g = grads[k]; d = dirs[k]
            sc = 1.2 / (np.linalg.norm(g) + 1e-9)
            ax.quiver(traj[k][0], traj[k][1], g[0]*sc, g[1]*sc,
                      scale=1, scale_units='xy', color=C_PRIMARY, width=0.005, zorder=12,
                      label=r'$\nabla f(x_k)$')
            ax.quiver(traj[k][0], traj[k][1], d[0]*sc, d[1]*sc,
                      scale=1, scale_units='xy', color=C_SUCCESS, width=0.005, zorder=12,
                      label=r'$d_k=-\nabla f(x_k)$')

        # Nota de ortogonalidad en el último frame
        if k == len(traj)-1 and len(dirs) >= 2:
            dot = float(np.dot(dirs[0], dirs[1]))
            note = f"$d_0 \\cdot d_1 \\approx {dot:.2f} \\approx 0$\n(direcciones ortogonales)"
            ax.text(0.03, 0.04, note, transform=ax.transAxes, fontsize=8, color=C_PURPLE,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#f5f3ff',
                              edgecolor=C_PURPLE, alpha=0.85))

        fval = float(f(traj[k]))
        title_k = "Inicio" if k == 0 else f"Iteracion {k}"
        ax.set_title(f"Maximo descenso - {title_k}\n"
                     f"$x_{k}={fmt_pt(traj[k])}$,  $f={fval:.2f}$",
                     color=C_TEXT, fontsize=10)
        ax.set_xlim(-3.5, 5); ax.set_ylim(-5, 4.5)
        ax.set_xlabel('$x$', fontsize=11); ax.set_ylabel('$y$', fontsize=11)
        ax.legend(loc='upper right', fontsize=8, frameon=True, facecolor='white', edgecolor='none')
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        plt.tight_layout()
        frames.append(fig_to_pil(fig))

        # Panel PDF
        ap = axes_pdf[k]
        ap.contour(X, Y, Z, levels=levels, colors='black', alpha=0.4, linewidths=0.8)
        for i in range(k + 1):
            is_last = (i == len(traj)-1) and (k == len(traj)-1)
            ap.plot(traj[i][0], traj[i][1], '*' if is_last else 'o',
                    color=C_SUCCESS if is_last else C_ALERT, markersize=8 if is_last else 5, zorder=10)
            ap.text(traj[i][0]+0.10, traj[i][1]+0.15, f'$x_{i}$', fontsize=7)
        for i in range(k):
            ap.annotate('', xy=traj[i+1], xytext=traj[i],
                        arrowprops=dict(arrowstyle='-|>', color=C_ALERT, lw=1.2, mutation_scale=10))
        if k < len(dirs):
            d = dirs[k]; sc = 0.9 / (np.linalg.norm(d) + 1e-9)
            ap.quiver(traj[k][0], traj[k][1], d[0]*sc, d[1]*sc,
                      scale=1, scale_units='xy', color=C_SUCCESS, width=0.008)
        ap.set_xlim(-3.5, 5); ap.set_ylim(-5, 4.5)
        ap.set_title(f"Iter. {k}", fontsize=9)
        ap.spines['top'].set_visible(False); ap.spines['right'].set_visible(False)
        plt.close(fig)

    gif_path = os.path.join(output_dir, "steepest_descent.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:],
                   optimize=False, duration=2000, loop=0)
    print(f"  Saved: {gif_path}")
    fig_pdf.suptitle(r"Maximo descenso: $f(x,y)=8x^2+3xy+7y^2-25x+31y-29$",
                     fontsize=12, color=C_TEXT, fontweight='bold')
    plt.tight_layout()
    pp = os.path.join(output_dir, "steepest_descent_pasos.png")
    fig_pdf.savefig(pp, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig_pdf)
    print(f"  Saved: {pp}")



if __name__ == '__main__':
    print("=== Generando animaciones de metodos multivariables ===")
    gen_coord_ciclicas_ej1_animation()
    gen_coord_ciclicas_ej2_animation()
    gen_steepest_descent_animation()
    print("=== Completado con exito ===")

