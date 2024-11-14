// Get the current page filename from the URL
const currentPage = window.location.pathname.split("/").pop();

// Map pages to their corresponding nav link IDs
const pageMap = {
  "index.html": "nav-household",
  "search.html": "nav-search",
};

// Check if the current page is in the pageMap and apply the active class
if (pageMap[currentPage]) {
  document.getElementById(pageMap[currentPage]).classList.add("active");
}

var plotData = {};

// Function to load the GMM clustering plot
function loadGMMPlot(width = 600, height = 450) {
  var jsonFile = "./clustering_plot/gmm_plot_k5.json";

  $.getJSON(jsonFile, function (data) {
    data.layout.width = width;
    data.layout.height = height;

    plotData["default-plot"] = data;
    plotData["filter-plot"] = JSON.parse(JSON.stringify(data));

    // Set initial colors for all points to grey in the filter plot
    plotData["filter-plot"].layout.title.text = "Node Embedding Visualization";
    const initialColorData = new Array(data.data[0].text.length).fill(
      "rgba(204, 204, 204, 0.1)"
    );
    plotData["filter-plot"].data[0].marker.color = initialColorData;

    Plotly.newPlot(
      "filtered_plot",
      plotData["filter-plot"].data,
      plotData["filter-plot"].layout
    );
  });
}

// Define the options for each attribute
const attributeValues = {
  income_level: { 1: "Less than 100,000฿/year", 2: "More than 100,000฿/year" },
  solid: { 0: "Non-solid", 1: "Solid" },
  dependent: [0, 1, 2, 3, 4, 5, 6],
  age: { 1: "0-6", 2: "6-12", 3: "12-18", 4: "18-60", 5: "More than 60" },
  disabled: { 0: "Non-disable", 1: "Disable" },
  prob_health: { 0: "No Problem", 1: "Has Problem" },
  prob_family: { 0: "No Problem", 1: "Has Problem" },
};

// Populate the second dropdown based on the selected attribute
$("#attr").on("change", function () {
  const selectedAttr = $(this).val();
  const values = attributeValues[selectedAttr] || {};

  const $attrVal = $("#attr-val");
  $attrVal
    .empty()
    .append('<option value="" disabled selected>Select Value</option>');

  // Use Object.entries to loop through the values object
  Object.entries(values).forEach(([key, value]) => {
    $attrVal.append(`<option value="${key}">${value}</option>`);
  });
});

let householdAttributes, hhMemberDict, memberAttributes;

// Load data files and parse them
async function loadData() {
  householdAttributes = await fetch("./data/household_attributes.json").then(
    (res) => res.json()
  );
  hhMemberDict = await fetch("./data/hh_member_dict.json").then((res) =>
    res.json()
  );
  memberAttributes = await fetch("./data/member_attributes.json").then((res) =>
    res.json()
  );
}

// Filter households based on selected attribute and value, then update plot
function filterHouseholds(attribute, value) {
  const matchingHouseholds = new Set();

  if (["income_level", "solid"].includes(attribute)) {
    // Household-level filtering
    for (const hh_id in householdAttributes) {
      const hhAttributes = householdAttributes[hh_id];
      if (
        attribute in hhAttributes &&
        hhAttributes[attribute] === Number(value)
      ) {
        matchingHouseholds.add("hh" + hh_id);
      }
    }
  } else if (["age", "disabled"].includes(attribute)) {
    // Member-level filtering
    for (const member_id in memberAttributes) {
      const memberData = memberAttributes[member_id];
      if (attribute in memberData && memberData[attribute] === Number(value)) {
        matchingHouseholds.add("hh" + memberData.hh); // Get the household ID from the member's data
      }
    }
  } else if (["prob_health", "prob_family"].includes(attribute)) {
    for (const member_id in memberAttributes) {
      const memberData = memberAttributes[member_id];
      if (value == 0 && !(attribute in memberData)) {
        matchingHouseholds.add("hh" + memberData.hh);
      } else if (
        value == 1 &&
        attribute in memberData &&
        memberData[attribute].length > 0
      ) {
        matchingHouseholds.add("hh" + memberData.hh);
      }
    }
  } else {
    // For No. of Dependent Members
    for (const hh_id in householdAttributes) {
      let dependentCount = 0;

      const members = hhMemberDict[hh_id] || [];
      for (const member_id of members) {
        const memberData = memberAttributes[member_id];

        // Define conditions for being a dependent
        const isDependent =
          memberData.age !== 4 ||
          memberData.disabled === 1 ||
          (memberData.prob_health &&
            [4, 8].some((code) => memberData.prob_health.includes(code))) ||
          (memberData.prob_family &&
            [14, 25].some((code) => memberData.prob_family.includes(code)));

        if (isDependent) dependentCount += 1;
      }
      if (dependentCount == value) matchingHouseholds.add("hh" + hh_id);
    }
  }

  // Update plot with matching households
  updateFilteredPlot([...matchingHouseholds]);
}

// Update the plot with filtered household IDs
function updateFilteredPlot(matchingHouseholds) {
  const colorData = plotData["filter-plot"].data[0].text.map((point) =>
    matchingHouseholds.includes(point) ? "#B90739" : "rgba(204, 204, 204, 0.1)"
  );

  plotData["filter-plot"].data[0].marker.color = colorData;
  Plotly.react(
    "filtered_plot",
    plotData["filter-plot"].data,
    plotData["filter-plot"].layout
  );

  console.log("Successfully Render!");
}

// Handle form submission
$('input[type="submit"]').on("click", function (event) {
  event.preventDefault();

  const attribute = $("#attr").val();
  const value = $("#attr-val").val();

  if (!attribute || !value) {
    alert("Please select both an attribute and a value.");
    return;
  }
  console.log(attribute, value);

  filterHouseholds(attribute, value);
});

// Toggle the default plot based on the checkbox state
$("#compare-ctr").change(function () {
  if (this.checked) {
    Plotly.newPlot(
      "compare_custering_plot",
      plotData["default-plot"].data,
      plotData["default-plot"].layout
    );
    $("#compare_custering_plot").show();
  } else {
    $("#compare_custering_plot").hide();
  }
});

// Load data on page load
$(document).ready(function () {
  loadGMMPlot();
  loadData();
});
