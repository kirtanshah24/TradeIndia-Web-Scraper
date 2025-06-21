import React from "react";
import { NavLink, Link } from "react-router-dom";
import { assets } from "../assets/assets";
import { FiSearch } from "react-icons/fi";

const Navbar = () => {
  return (
    <nav className="w-full bg-white shadow-md border-b fixed top-0 left-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo Section */}
          <div className="flex-shrink-0">
            <NavLink to="/" className="flex items-center gap-2">
              <img src={assets.logo} alt="Logo" className="w-8 h-8" />
              <span className="text-lg font-bold text-gray-700">TradeIndia Web Scraper</span>
            </NavLink>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex space-x-6">
            <NavLink
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 text-sm transition-all duration-300 ${
                  isActive ? "text-[#ABCDEF] font-semibold border-b-2 border-[#ABCDEF]" : "text-gray-700 hover:text-[#ABCDEF]"
                }`
              }
              to="/"
            >
              <img src={assets.home_icon} alt="Home" className="w-5 h-5" />
              <p>Home</p>
            </NavLink>


            <NavLink
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 text-sm transition-all duration-300 ${
                  isActive ? "text-[#ABCDEF] font-semibold border-b-2 border-[#ABCDEF]" : "text-gray-700 hover:text-[#ABCDEF]"
                }`
              }
              to="/suppliers"
            >
              <img src={assets.about_icon} alt="About" className="w-5 h-5" />
              <p>Supplier Listings</p>
            </NavLink>

            <Link to="/search" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
              <FiSearch className="w-5 h-5" />
              <span>Search Products</span>
            </Link>
          </div>

          {/* Mobile Menu Placeholder (Future Enhancement) */}
          <div className="md:hidden">
            {/* Add a hamburger menu icon for mobile responsiveness */}
          </div>

        </div>
      </div>
    </nav>
  );
};

export default Navbar;
