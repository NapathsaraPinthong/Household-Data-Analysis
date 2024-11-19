var plotData = {};

// Function to load the selected clustering plot and highlight the selected button
function loadPlot(plotId, width = 600, height = 450) {
  var plotFileMap = {
    "gmm-plot": "./clustering_plot/gmm_plot_k5.json",
    "kmeans-plot": "./clustering_plot/kmeans_plot_k6.json",
    "hierarchical-plot": "./clustering_plot/hierarchical_plot_k6.json",
  };
  var jsonFile = plotFileMap[plotId];

  // Remove "active" class from all buttons and add it to the clicked button
  $(".select-clustering button").removeClass("active");
  $(`button[onclick="loadPlot('${plotId}')"]`).addClass("active");

  // Load and render the clustering plot
  $.getJSON(jsonFile, function (data) {
    plotData[plotId] = data;
    // Update layout size
    data.layout.width = width;
    data.layout.height = height;
    Plotly.newPlot("clustering_plot", data.data, data.layout);
  });
}

// Load the fragile level plot when the checkbox is checked
function loadFragileLevelPlot(width = 600, height = 450) {
  var fragileLevelFile = "./clustering_plot/fragile_level_visualization.json";

  $.getJSON(fragileLevelFile, function (data) {
    plotData["fg-plot"] = data;
    // Update layout size
    data.layout.width = width;
    data.layout.height = height;
    Plotly.newPlot("fragile_plot", data.data, data.layout);
  });
}

// Toggle the fragile level plot based on the checkbox state
$("#compare-fg").change(function () {
  if (this.checked) {
    loadFragileLevelPlot();
    $("#fragile_plot").show();
  } else {
    $("#fragile_plot").hide();
  }
});

// Initialize with a default clustering plot and highlight the default button
loadPlot("gmm-plot");

// Get the current page filename from the URL
const currentPage = window.location.pathname.split("/").pop();

// Map pages to their corresponding nav link IDs
const pageMap = {
  "": "nav-household",
  search: "nav-search",
};

// Check if the current page is in the pageMap and apply the active class
if (pageMap[currentPage]) {
  document.getElementById(pageMap[currentPage]).classList.add("active");
}
