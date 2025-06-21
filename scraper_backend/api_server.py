from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dynamicProductScraper import DynamicTradeIndiaScraper
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import io
import tempfile

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize scraper
try:
    scraper = DynamicTradeIndiaScraper()
    logger.info("✅ Scraper initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize scraper: {e}")
    scraper = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scraper_ready": scraper is not None,
        "api_key_configured": bool(os.getenv('SERPAPI_KEY'))
    })

@app.route('/api/search', methods=['POST'])
def search_products():
    """Search for products by name."""
    if not scraper:
        return jsonify({"error": "Scraper not initialized"}), 500
    
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()
        max_results = data.get('max_results', 30)
        include_detailed_info = data.get('include_detailed_info', True)
        
        if not product_name:
            return jsonify({"error": "Product name is required"}), 400
        
        logger.info(f"🔍 Searching for product: {product_name}")
        
        # Perform the search
        results = scraper.scrape_product(
            product_name=product_name,
            max_results=max_results,
            include_detailed_info=include_detailed_info
        )
        
        if "error" in results:
            return jsonify(results), 404
        
        # Add API response metadata
        results["api_version"] = "1.0"
        results["request_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"✅ Search completed for '{product_name}': {results['total_results']} results")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"❌ Error in search endpoint: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/search', methods=['GET'])
def search_products_get():
    """Search for products using GET method (for testing)."""
    if not scraper:
        return jsonify({"error": "Scraper not initialized"}), 500
    
    try:
        product_name = request.args.get('product_name', '').strip()
        max_results = int(request.args.get('max_results', 30))
        include_detailed_info = request.args.get('include_detailed_info', 'true').lower() == 'true'
        
        if not product_name:
            return jsonify({"error": "Product name is required"}), 400
        
        logger.info(f"🔍 Searching for product: {product_name}")
        
        results = scraper.scrape_product(
            product_name=product_name,
            max_results=max_results,
            include_detailed_info=include_detailed_info
        )
        
        if "error" in results:
            return jsonify(results), 404
        
        results["api_version"] = "1.0"
        results["request_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"✅ Search completed for '{product_name}': {results['total_results']} results")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"❌ Error in search endpoint: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/download', methods=['POST'])
def download_results():
    """Download search results as Excel or JSON file."""
    if not scraper:
        return jsonify({"error": "Scraper not initialized"}), 500
    
    try:
        data = request.get_json()
        results = data.get('results')
        format_type = data.get('format', 'excel')  # 'excel' or 'json'
        
        if not results or not results.get('products'):
            return jsonify({"error": "No results to download"}), 400
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        product_name = results.get('product_name', 'products')
        
        if format_type == 'excel':
            # Generate Excel file in memory
            excel_data = scraper.generate_excel_data(results)
            if not excel_data:
                return jsonify({"error": "Failed to generate Excel data"}), 500
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(excel_data)
                tmp_file_path = tmp_file.name
            
            filename = f"tradeindia_{product_name}_{timestamp}.xlsx"
            
            return send_file(
                tmp_file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        elif format_type == 'json':
            # Generate JSON data
            json_data = scraper.generate_json_data(results)
            if not json_data:
                return jsonify({"error": "Failed to generate JSON data"}), 500
            
            filename = f"tradeindia_{product_name}_{timestamp}.json"
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w', encoding='utf-8') as tmp_file:
                tmp_file.write(json_data)
                tmp_file_path = tmp_file.name
            
            return send_file(
                tmp_file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/json'
            )
        else:
            return jsonify({"error": "Invalid format. Use 'excel' or 'json'"}), 400
        
    except Exception as e:
        logger.error(f"❌ Error in download endpoint: {e}")
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f" Starting Flask API server on port {port}")
    print(f" Debug mode: {debug}")
    print(f" API Key configured: {'Yes' if os.getenv('SERPAPI_KEY') else 'No'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 