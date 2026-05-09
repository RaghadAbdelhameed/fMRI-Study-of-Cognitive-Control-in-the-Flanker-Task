import os
import sys
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from nilearn import plotting, datasets, surface

def create_brain_report(stat_map_path, output_name, title):
    # Absolute Path for saving
    save_dir = "/mnt/d/Third-Year/Second-Term/Flanker-task-dataset/ds000102-download"
    surf_out = os.path.join(save_dir, f"{output_name}_surface.png")
    int_out = os.path.join(save_dir, f"{output_name}_internal.png")

    print(f"--- Processing: {title} ---")
    
    if not os.path.exists(stat_map_path):
        print(f"Error: {stat_map_path} not found.")
        return

    fsaverage = datasets.fetch_surf_fsaverage()
    texture_l = surface.vol_to_surf(stat_map_path, fsaverage.pial_left)
    texture_r = surface.vol_to_surf(stat_map_path, fsaverage.pial_right)
    
    # Constants for the Color Map
    z_min = 3.1
    z_max = 8.0
    cmap_name = 'cold_hot' # Blue-White-Red

    # 1. GENERATE SURFACE FIGURE
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), subplot_kw={'projection': '3d'}, facecolor='white')
    axes = axes.flatten()
    
    views = ['lateral', 'medial', 'lateral', 'medial']
    hemis = ['left', 'left', 'right', 'right']
    
    for i, (view, hemi) in enumerate(zip(views, hemis)):
        tex = texture_l if hemi == 'left' else texture_r
        mesh = fsaverage.pial_left if hemi == 'left' else fsaverage.pial_right
        bg = fsaverage.sulc_left if hemi == 'left' else fsaverage.sulc_right
        
        plotting.plot_surf_stat_map(
            mesh, tex, hemi=hemi, view=view,
            bg_map=bg, threshold=z_min, cmap=cmap_name,
            axes=axes[i], colorbar=False # We add our own below
        )
        axes[i].set_title(f"{hemi.capitalize()} {view.capitalize()}", fontsize=14, pad=0)
    
    # --- ADD THE COLORBAR (THRESHOLD MAP) ---
    # Create a separate axis at the bottom for the colorbar
    cbar_ax = fig.add_axes([0.3, 0.08, 0.4, 0.02]) # [left, bottom, width, height]
    norm = mcolors.Normalize(vmin=z_min, vmax=z_max)
    sm = plt.cm.ScalarMappable(cmap=cmap_name, norm=norm)
    cb = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal', extend='both')
    cb.set_label('Z-Statistic Threshold', fontsize=12, fontweight='bold')

    plt.suptitle(title, fontsize=22, y=0.95, fontweight='bold')
    plt.savefig(surf_out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"SUCCESS: Surface view saved with Colorbar.")

    # 2. GENERATE INTERNAL SLICE FIGURE
    # Nilearn's plot_stat_map adds its own colorbar by default
    display = plotting.plot_stat_map(
        stat_map_path, display_mode='z', cut_coords=8,
        threshold=z_min, title=f"{title} (Internal)", 
        cmap=cmap_name, colorbar=True
    )
    display.savefig(int_out)
    display.close()
    print(f"SUCCESS: Internal view saved.")

if __name__ == "__main__":
    create_brain_report(sys.argv[1], sys.argv[2], sys.argv[3])
