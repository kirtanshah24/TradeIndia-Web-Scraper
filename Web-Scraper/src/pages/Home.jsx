import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import * as XLSX from "xlsx";
import Carousel from "../components/carousel"; 

const Home = () => {
  const navigate = useNavigate();

  const [searchParams, setSearchParams] = useState({
    industry: "",
    location: "",
    experience: "", 
  });

  const [industryTypes, setIndustryTypes] = useState([]);

  // ✅ Fetch unique industry types from the Excel file
  useEffect(() => {
    const fetchIndustryTypes = async () => {
      try {
        const response = await fetch("/data.xlsx");
        const buffer = await response.arrayBuffer();
        const workbook = XLSX.read(buffer, { type: "array" });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const parsedData = XLSX.utils.sheet_to_json(sheet);

        // Extract unique industry types
        const uniqueIndustries = [...new Set(parsedData.map((item) => item["Industry Type"] || "Unknown"))];
        setIndustryTypes(["All", ...uniqueIndustries]); // ✅ Include "All" option

      } catch (error) {
        console.error("Error fetching industry types:", error);
      }
    };

    fetchIndustryTypes();
  }, []);

  const handleChange = (e) => {
    setSearchParams({
      ...searchParams,
      [e.target.name]: e.target.value,
    });
  };

  const handleSearch = () => {
    const queryString = new URLSearchParams(searchParams).toString();
    navigate(`/suppliers?${queryString}`); // ✅ Redirect to About.js with filters
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      
      {/* ✅ Display the Carousel above the search bar */}
      <Carousel />

      {/* Title */}
      <h1 className="text-2xl font-bold text-gray-900 mt-5 mb-6">🔍 Find Suppliers</h1>

      {/* Search Bar in a Single Line */}
      <div className="bg-white shadow-md rounded-lg p-4 w-full max-w-5xl flex items-center justify-between gap-3 flex-wrap">
        
        {/* Industry Dropdown (Fetched from Excel) */}
        <select
          name="industry"
          value={searchParams.industry}
          onChange={handleChange}
          className="flex-1 p-3 border rounded-lg focus:ring focus:ring-blue-300 min-w-[180px]"
        >
          {industryTypes.map((industry, index) => (
            <option key={index} value={industry}>
              {industry}
            </option>
          ))}
        </select>

        {/* Location Input */}
        <input
          type="text"
          name="location"
          value={searchParams.location}
          onChange={handleChange}
          placeholder="📍 Enter Location"
          className="flex-1 p-3 border rounded-lg focus:ring focus:ring-blue-300 min-w-[180px]"
        />

        {/* Experience Dropdown */}
        <select
          name="experience"
          value={searchParams.experience}
          onChange={handleChange}
          className="flex-1 p-3 border rounded-lg focus:ring focus:ring-blue-300 min-w-[180px]"
        >
          <option value="">🎯 Experience</option>
          <option value="5">5+ Years</option>
          <option value="10">10+ Years</option>
          <option value="20">20+ Years</option>
          <option value="30">30+ Years</option>
          <option value="50">50+ Years</option>
          <option value="80">80+ Years</option>
        </select>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          className="bg-blue-600 text-white px-3 py-3 rounded-lg font-medium shadow-md hover:bg-blue-700 transition min-w-[120px]"
        >
          🔍 Search
        </button>
      </div>
    </div>
  );
};

export default Home;
