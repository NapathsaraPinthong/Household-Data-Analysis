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
  prob_health: {
    1: "HIV/AIDS",
    2: "Age-related forgetfulness",
    3: "Affected by AIDS",
    4: "Bedridden patient",
    5: "Serious illness",
    6: "Chronic illness",
    7: "Lack of physical equipment/no disability aids",
    8: "Unable to help oneself in daily life",
    9: "Not receiving medical treatment or rehabilitation",
    10: "Drug addiction",
    11: "Mental patient",
    12: "Depression",
    13: "No right to medical treatment",
  },
  prob_family: { 
    1: "Orphan",
    2: "Broken family/parents separated",
    3: "Foster family",
    4: "Inappropriate upbringing",
    5: "Affected by family members being imprisoned",
    6: "Have to take care of family members",
    7: "Have to take on family responsibilities beyond their age/intellectual abilities",
    8: "Pregnant out of wedlock",
    9: "Pregnant as a teenager and not ready to raise a child",
    10: "Abandoned",
    11: "Living alone without caregiver and have problems in making a living",
    12: "Parents or caregivers have inappropriate behavior",
    13: "Parents or caregivers cannot provide for the child",
    14: "Widowers who have to raise their children alone/single fathers",
    15: "No caregivers during the day, the caregiver has to go out to work outside the home",
    16: "No caregivers at night, have to go out to work outside the home",
    17: "Cannot raise the child",
    18: "The family has debts",
    19: "The family has the burden of supporting people with problems",
    20: "The benefactor is poor/in need",
    21: "The family is poor",
    22: "Behaving inappropriately",
    23: "Risk of wrongdoing",
    24: "Do not know how to behave or adjust appropriately",
    25: "Widows who have to raise children alone/Single mothers",
  },
};

// Populate the second dropdown based on the selected attribute
$("#attr").on("change", function () {
  const selectedAttrCon = document.getElementById("select-attribute-con")
  const selectedAttr = $(this).val();
  const values = attributeValues[selectedAttr] || {};

  const $attrValContainer = $("#attr-val-container"); 
  $attrValContainer.empty();

  if (selectedAttr === "prob_health" || selectedAttr === "prob_family") {
    Object.entries(values).forEach(([key, value]) => {
      $attrValContainer.append(`
        <div>
          <input type="checkbox" id="${key}" value="${key}" name="prob">
          <label for="${key}">${value}</label>
        </div>
      `);
    });

    selectedAttrCon.classList.add("multiple")

  } else {
    // Create a single-select dropdown for other attributes
    const $select = $('<select id="attr-val"></select>').append(
      '<option value="" disabled selected>Select Value</option>'
    );
    Object.entries(values).forEach(([key, value]) => {
      $select.append(`<option value="${key}">${value}</option>`);
    });

    $attrValContainer.append($select);
    selectedAttrCon.classList.remove("multiple")
  }
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
function filterHouseholds(attribute, values) {
  const matchingHouseholds = new Set();

  // Convert single value to array for consistency
  if (!Array.isArray(values)) {
    values = [values];
  }

  if (["income_level", "solid"].includes(attribute)) {
    // Household-level filtering
    for (const hh_id in householdAttributes) {
      const hhAttributes = householdAttributes[hh_id];
      if (
        attribute in hhAttributes &&
        hhAttributes[attribute] === Number(values)
      ) {
        matchingHouseholds.add("hh" + hh_id);
      }
    }
  } else if (["age", "disabled"].includes(attribute)) {
    // Member-level filtering
    for (const member_id in memberAttributes) {
      const memberData = memberAttributes[member_id];
      if (attribute in memberData && memberData[attribute] === Number(values)) {
        matchingHouseholds.add("hh" + memberData.hh); // Get the household ID from the member's data
      }
    }
  } else if (["prob_health", "prob_family"].includes(attribute)) {
    const selectedValues = values.map(Number);
    for (const member_id in memberAttributes) {
      const memberData = memberAttributes[member_id];
      if (
        attribute in memberData &&
        memberData[attribute].some((issue) => selectedValues.includes(issue))
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
      if (dependentCount == values) matchingHouseholds.add("hh" + hh_id);
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
  const $attrValContainer = $("#attr-val-container");

  let selectedValues;

  if (attribute === "prob_health" || attribute === "prob_family") {
    // Collect checked checkbox values
    selectedValues = $attrValContainer
      .find('input[name="prob"]:checked')
      .map(function () {
        return this.value;
      })
      .get();
  } else {
    // Collect the dropdown value
    selectedValues = $attrValContainer.find("select").val();
  }

  if (!attribute || !selectedValues || selectedValues.length === 0) {
    alert("Please select both an attribute and a value.");
    return;
  }

  console.log(attribute, selectedValues);

  filterHouseholds(attribute, selectedValues);
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
