import React, { useState, useEffect } from "react";
import * as XLSX from "xlsx";
import { useLocation } from "react-router-dom"; // To access URL params

const Suppliers = () => {
  const location = useLocation();
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [industryTypes, setIndustryTypes] = useState([]);
  const [selectedIndustry, setSelectedIndustry] = useState("All");
  const [locationInput, setLocationInput] = useState("");
  const [selectedExperience, setSelectedExperience] = useState(""); // Experience filter

  // Function to Load Excel Data
  const loadExcelData = async () => {
    try {
      const response = await fetch("/data.xlsx");
      const buffer = await response.arrayBuffer();
      const workbook = XLSX.read(buffer, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const parsedData = XLSX.utils.sheet_to_json(sheet);

      // Calculate Experience (Current Year - Established Year)
      const currentYear = new Date().getFullYear();
      const transformedData = parsedData.map((item) => ({
        ...item,
        Experience: item["Established Year"]
          ? currentYear - parseInt(item["Established Year"], 10)
          : "N/A",
      }));

      setData(transformedData);
      setFilteredData(transformedData);

      // Extract unique Industry Types for filtering
      const uniqueIndustries = [
        ...new Set(transformedData.map((item) => item["Industry Type"] || "Unknown")),
      ];
      setIndustryTypes(["All", ...uniqueIndustries]); // Include "All" option
    } catch (error) {
      console.error("Error loading Excel data:", error);
    }
  };

  useEffect(() => {
    loadExcelData();
  }, []);

  // Filter data dynamically based on URL parameters
  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const industryFilter = queryParams.get("industry") || "All";
    const locationFilter = queryParams.get("location") || "";
    const experienceFilter = queryParams.get("experience") || "";

    setSelectedIndustry(industryFilter);
    setLocationInput(locationFilter);
    setSelectedExperience(experienceFilter);
  }, [location.search]);

  // Apply filters dynamically based on the selected filters
  useEffect(() => {
    let filtered = data;

    if (selectedIndustry !== "All") {
      filtered = filtered.filter((item) => item["Industry Type"] === selectedIndustry);
    }

    if (locationInput.trim() !== "") {
      filtered = filtered.filter((item) =>
        item["Location"].toLowerCase().includes(locationInput.toLowerCase())
      );
    }

    if (selectedExperience !== "") {
      const minYears = parseInt(selectedExperience, 10);
      filtered = filtered.filter(
        (item) => item.Experience !== "N/A" && item.Experience >= minYears
      );
    }

    setFilteredData(filtered);
  }, [selectedIndustry, locationInput, selectedExperience, data]);

  return (
    <div className="p-8 min-h-screen bg-gray-100 mt-5">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">🏭 Supplier Listings</h1>

      {/* Filters Section */}
      <div className="flex flex-wrap gap-4 mb-6 bg-white p-4 shadow-md rounded-lg">
        {/* Industry Filter Dropdown */}
        <div>
          <label className="text-gray-700 font-medium">Filter by Industry:</label>
          <select
            className="ml-3 p-2 border border-gray-300 rounded-lg bg-white shadow-md"
            value={selectedIndustry}
            onChange={(e) => setSelectedIndustry(e.target.value)}
          >
            {industryTypes.map((industry, index) => (
              <option key={index} value={industry}>
                {industry}
              </option>
            ))}
          </select>
        </div>

        {/* Location Filter Input */}
        <div>
          <label className="text-gray-700 font-medium">Search by Location:</label>
          <input
            type="text"
            placeholder="Type city or state..."
            className="ml-3 p-2 border border-gray-300 rounded-lg bg-white shadow-md w-60"
            value={locationInput}
            onChange={(e) => setLocationInput(e.target.value)}
          />
        </div>

        {/* Experience Filter Dropdown */}
        <div>
          <label className="text-gray-700 font-medium">Filter by Experience:</label>
          <select
            className="ml-3 p-2 border border-gray-300 rounded-lg bg-white shadow-md"
            value={selectedExperience}
            onChange={(e) => setSelectedExperience(e.target.value)}
          >
            <option value="">All</option>
            <option value="5">5+ Years</option>
            <option value="10">10+ Years</option>
            <option value="20">20+ Years</option>
            <option value="30">30+ Years</option>
            <option value="50">50+ Years</option>
            <option value="80">80+ Years</option>
          </select>
        </div>
      </div>

      {/* Display Filtered Data in Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {filteredData.length > 0 ? (
          filteredData.map((item, index) => (
            <div
              key={index}
              className="border border-gray-300 rounded-2xl shadow-md p-6 bg-white hover:shadow-xl transition-transform duration-300 transform hover:scale-105"
            >
              {/* Industry Name */}
              <h3 className="text-sm font-bold text-white bg-blue-500 px-3 py-1 rounded-full w-fit mb-2">
                {item["Industry Type"] || "Unknown Industry"}
              </h3>

              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                {item["Company Name"]}
              </h2>
              <hr className="border-gray-300 mb-3" />

              {/* Product Details */}
              <p className="text-gray-700 text-lg">
                🏷 <span className="font-medium">{item["Product Name"]}</span>
              </p>
              <p className="text-gray-700 text-lg">
                📍 <span className="font-medium">{item["Location"]}</span>
              </p>
              <p className="text-gray-700 text-lg">
                🗓 <span className="font-medium">Established in {item["Established Year"]}</span>
              </p>
              <p className="text-gray-700 text-lg">
                🎯 <span className="font-medium">{item.Experience} years of experience</span>
              </p>

              <p
                className={`text-lg font-medium ${
                  item["Trust Status"] === "Trusted Seller"
                    ? "text-green-600"
                    : "text-red-600"
                }`}
              >
                {item["Trust Status"] === "Trusted Seller"
                  ? "✅ Verified Supplier"
                  : "⚠️ Not Verified"}
              </p>

              {/* Links */}
              <div className="mt-4">
                <a
                  href={item["Product Link"]}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium shadow-md hover:bg-blue-700"
                >
                  View Product
                </a>
              </div>
            </div>
          ))
        ) : (
          <p className="text-gray-500">No suppliers found for the selected filters.</p>
        )}
      </div>
    </div>
  );
};

export default Suppliers;
