import json
import pandas as pd
import numpy as np


def update_colors_based_on_fg_level(
    kmeans_json_path, fg_level_file_path, output_json_path
):
    # Load the KMeans plot JSON file
    with open(kmeans_json_path, "r") as f:
        kmeans_data = json.load(f)

    # Load fg_level data
    fg_level_df = pd.read_excel(
        fg_level_file_path, header=None, names=["hh", "fg_level"]
    )
    fg_level_df["node_id"] = "hh" + fg_level_df["hh"].astype(str)

    # Extract `node_id` from the KMeans JSON
    node_ids = kmeans_data["data"][0]["text"]

    # Map `fg_level` to node IDs
    node_fg_map = dict(zip(fg_level_df["node_id"], fg_level_df["fg_level"]))

    # Replace the color in the JSON with `fg_level` values
    fg_levels = [
        node_fg_map.get(node_id, -1) for node_id in node_ids
    ]  # Default to -1 if `node_id` not found

    # Update colors in the JSON data
    kmeans_data["data"][0]["marker"][
        "color"
    ] = fg_levels  # Use actual `fg_level` values

    # Create a custom colorscale that maps fg_level directly to the desired range
    unique_fg_levels = sorted(set(fg_levels))
    num_fg_levels = len(unique_fg_levels)
    colorscale = [
        [i / (num_fg_levels - 1), color]
        for i, color in enumerate(
            [
                "#440154",  # Dark purple (low end of Viridis)
                "#31688e",  # Blue
                "#35b779",  # Green
                "#fde725",  # Yellow (high end of Viridis)
                "#ff5733",  # Optional: Add more distinct colors if needed
            ][:num_fg_levels]
        )
    ]

    # Update the coloraxis with fg_levels in the colorbar
    kmeans_data["layout"]["coloraxis"] = {
        "colorbar": {
            "title": "Fragile Levels",
            "tickvals": unique_fg_levels,  # Show actual `fg_level` values on the colorbar
            "ticktext": [
                str(level) for level in unique_fg_levels
            ],  # Convert to string for readability
        },
        "colorscale": colorscale,
    }

    # Update plot title
    kmeans_data["layout"]["title"]["text"] = "Fragile Level Visualization"

    # Save the updated JSON to the output file
    with open(output_json_path, "w") as f:
        json.dump(kmeans_data, f)

    print(f"Updated plot JSON saved to '{output_json_path}'")


# Example usage:
update_colors_based_on_fg_level(
    kmeans_json_path="../pages/clustering_plot/kmeans_plot_k8.json",
    fg_level_file_path="../data/dataset/edge/hh-fg_level.xlsx",
    output_json_path="../pages/clustering_plot/fg_level_plot.json",
)
