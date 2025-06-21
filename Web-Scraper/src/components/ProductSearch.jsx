import React, { useState } from 'react';
import { FiSearch, FiDownload, FiLoader, FiExternalLink } from 'react-icons/fi';

const ProductSearch = () => {
  const [productName, setProductName] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [maxResults, setMaxResults] = useState(20);
  const [downloading, setDownloading] = useState(false);

  // API base URL - change this to your server URL
  const API_BASE_URL = 'http://localhost:5000/api';

  const handleSearch = async () => {
    if (!productName.trim()) {
      setError('Please enter a product name');
      return;
    }

    setLoading(true);
    setError(null);
    setSearchResults(null);

    try {
      console.log('🔍 Searching for:', productName);
      
      const response = await fetch(`${API_BASE_URL}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_name: productName.trim(),
          max_results: maxResults,
          include_detailed_info: true
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Search failed');
      }

      console.log('✅ Search results:', data);
      setSearchResults(data);
    } catch (err) {
      console.error('❌ Search error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (format) => {
    if (!searchResults) return;

    setDownloading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          results: searchResults,
          format: format
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Download failed');
      }

      // Get the filename from the response headers
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `tradeindia_${searchResults.product_name}_${new Date().toISOString().slice(0,10)}.${format}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Create a blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      console.log(`✅ Downloaded ${filename}`);
    } catch (err) {
      console.error('❌ Download error:', err);
      alert(`Download failed: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Search Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">
          🔍 Search TradeIndia Suppliers
        </h2>
        
        <div className="flex flex-col lg:flex-row gap-4 mb-4">
          <div className="flex-1">
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter product name (e.g., aluminium, steel, plastic, copper)"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            />
          </div>
          
          <div className="w-full lg:w-48">
            <select
              value={maxResults}
              onChange={(e) => setMaxResults(parseInt(e.target.value))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={10}>10 results</option>
              <option value={20}>20 results</option>
              <option value={30}>30 results</option>
              <option value={50}>50 results</option>
            </select>
          </div>
          
          <button
            onClick={handleSearch}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-8 py-3 rounded-lg flex items-center justify-center gap-2 transition-colors text-lg font-semibold"
          >
            {loading ? (
              <>
                <FiLoader className="animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <FiSearch />
                Search
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>

      {/* Results Section */}
      {searchResults && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6 gap-4">
            <div>
              <h3 className="text-2xl font-semibold text-gray-800">
                Search Results for "{searchResults.product_name}"
              </h3>
              <p className="text-gray-600 mt-2">
                Found {searchResults.total_results} suppliers • 
                Scraped at {new Date(searchResults.scraped_at).toLocaleString()}
              </p>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => handleDownload('excel')}
                disabled={downloading}
                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center gap-2"
              >
                {downloading ? (
                  <FiLoader className="animate-spin" />
                ) : (
                  <FiDownload />
                )}
                Download Excel
              </button>
              <button
                onClick={() => handleDownload('json')}
                disabled={downloading}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center gap-2"
              >
                {downloading ? (
                  <FiLoader className="animate-spin" />
                ) : (
                  <FiDownload />
                )}
                Download JSON
              </button>
            </div>
          </div>

          {/* Results Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {searchResults.products.map((product, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow bg-gray-50">
                <h4 className="font-semibold text-gray-800 mb-3 line-clamp-2 text-lg">
                  {product['Product Name']}
                </h4>
                
                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  <div className="flex justify-between">
                    <span className="font-medium">Supplier:</span>
                    <span className="truncate text-right">{product['Company Name'] || product['Supplier']}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="font-medium">Location:</span>
                    <span className="text-right">{product['Location']}</span>
                  </div>
                  
                  {product['Price (INR)'] && product['Price (INR)'] !== 'N/A' && (
                    <div className="flex justify-between">
                      <span className="font-medium">Price:</span>
                      <span className="text-green-600 font-semibold text-right">{product['Price (INR)']}</span>
                    </div>
                  )}
                  
                  {product['Trust Status'] && (
                    <div className="flex justify-between items-center">
                      <span className="font-medium">Trust Status:</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        product['Trust Status'] === 'Trusted Seller' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {product['Trust Status']}
                      </span>
                    </div>
                  )}
                  
                  {product['Established Year'] && product['Established Year'] !== 'N/A' && (
                    <div className="flex justify-between">
                      <span className="font-medium">Established:</span>
                      <span className="text-right">{product['Established Year']}</span>
                    </div>
                  )}
                </div>
                
                <div className="pt-3 border-t border-gray-200">
                  <a
                    href={product['Product Link']}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-1"
                  >
                    <FiExternalLink />
                    View on TradeIndia
                  </a>
                </div>
              </div>
            ))}
          </div>

          {searchResults.products.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>No products found for "{searchResults.product_name}"</p>
              <p className="text-sm mt-2">Try searching for a different product or check your spelling.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ProductSearch; 