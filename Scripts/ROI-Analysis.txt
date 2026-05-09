#!/bin/bash

# ==========================================
# ROI Analysis Automation Script
# ==========================================

STATS_DIR="Flanker_2ndLevel.gfeat/cope3.feat/stats"
STANDARD_BRAIN="$FSLDIR/data/standard/MNI152_T1_2mm.nii.gz"

echo "=== Starting ROI Analysis Automation ==="

# 1. Check for the merged Z-stats file
if [ ! -f "allZstats.nii.gz" ]; then
    echo "-> allZstats.nii.gz not found. Merging from $STATS_DIR..."
    if [ -d "$STATS_DIR" ]; then
        fslmerge -t allZstats.nii.gz $(ls ${STATS_DIR}/zstat*.nii.gz | sort -V)
        echo "-> allZstats.nii.gz created successfully."
    else
        echo "ERROR: $STATS_DIR does not exist. Check your path."
        exit 1
    fi
else
    echo "-> allZstats.nii.gz already exists. Skipping merge."
fi

# 2. Define the regions from your image
# Format: "RegionName Voxel_X Voxel_Y Voxel_Z Radius_in_mm"
# Note: These MNI coordinates have been converted to 2mm Voxel coordinates for FSL
declare -a regions=(
    "Fusiform_Gyrus_Right 28 37 28 5"      # MNI: 34 -52 -16
    "LOC_sup_Right 29 36 49 5"             # MNI: 32 -54 26
    "PCG 27 62 60 5"                       # MNI: 36 -2 48
    "LOC_inf_Right1 34 39 27 5"            # MNI: 22 -48 -18
    "Fusiform_Gyrus_Left 63 59 28 5"       # MNI: -36 -8 -16
    "LOC_sup_Left 61 33 47 5"              # MNI: -32 -60 22
    "Insular_Cortex_Left 59 64 30 5"       # MNI: -28 2 -12
    "LOC_inf_Right2 19 32 34 5"            # MNI: 52 -62 -4
)

# 3. Loop through each region to create masks and extract stats
echo "=== Generating Masks and Extracting Stats ==="

for region_info in "${regions[@]}"; do
    # Read the variables from the array string
    read -r name x y z radius <<< "$region_info"
    
    echo "Processing $name at voxel coords ($x, $y, $z)..."
    
    # Step A: Create a single voxel point at the coordinates
    fslmaths "$STANDARD_BRAIN" -mul 0 -add 1 -roi $x 1 $y 1 $z 1 0 1 "ROI_${name}.nii.gz" -odt float
    
    # Step B: Expand the point into a sphere
    fslmaths "ROI_${name}.nii.gz" -kernel sphere $radius -fmean "Sphere_${name}.nii.gz" -odt float
    
    # Step C: Binarize the spherical mask
    fslmaths "Sphere_${name}.nii.gz" -bin "Sphere_bin_${name}.nii.gz"
    
    # Step D: Extract the mean time series (z-stats) from the mask
    fslmeants -i allZstats.nii.gz -m "Sphere_bin_${name}.nii.gz" > "Stats_${name}.txt"
    
    echo "-> Saved extracted data to Stats_${name}.txt"
    echo "----------------------------------------"
done

echo "=== All ROI analyses completed successfully! ==="
