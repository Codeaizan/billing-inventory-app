"""
Script to import all products from Natural Health World rate list
Run this once to populate the database with all products
"""

from database.db_manager import db
from modules.inventory import inventory_manager
from utils.logger import logger

# Product data from rate list
PRODUCTS = [
    # Format: (name, package_size, mrp, category, unit)
    
    # Capsules
    ("Karishmai Capsule", "30 Nos", 250, "Capsules", "Nos"),
    ("Karishmai Capsule", "60 Nos", 480, "Capsules", "Nos"),
    ("Karishmai Oil", "120 ml", 280, "Oils", "ml"),
    ("Karishmai Oil", "60 ml", 150, "Oils", "ml"),
    ("Ortho Care Plus Awaleh", "250 gm", 430, "Awaleh/Powder", "gm"),
    ("Spondylimed Pills", "60 Nos", 300, "Pills", "Nos"),
    ("Diabo Guard Capsule", "60 Nos", 560, "Capsules", "Nos"),
    ("Diabo Guard Booster Capsule", "60 Nos", 490, "Capsules", "Nos"),
    ("Pilexomed Capsule", "30 Nos", 340, "Capsules", "Nos"),
    ("Pilexomed Awaleh", "250 gm", 410, "Awaleh/Powder", "gm"),
    ("Pilexomed Ointment", "50 gm", 190, "Ointment", "gm"),
    ("Azma Care Plus Capsule", "30 Nos", 460, "Capsules", "Nos"),
    ("Azma Care Plus Awaleh", "125 gm", 330, "Awaleh/Powder", "gm"),
    ("Azma Care Plus Awaleh", "250 gm", 630, "Awaleh/Powder", "gm"),
    ("Heart Care Plus Capsule", "30 Nos", 490, "Capsules", "Nos"),
    ("Aloe Moringa", "60 Nos", 740, "Capsules", "Nos"),
    ("Leukoria Niwaran Capsule", "30 Nos", 430, "Capsules", "Nos"),
    ("Calcium Magnesium Zinc", "30 Nos", 380, "Capsules", "Nos"),
    ("Glocosamine Capsule", "30 Nos", 540, "Capsules", "Nos"),
    ("Sllim Youu Capsule", "60 Nos", 1150, "Capsules", "Nos"),
    ("Livo Amrit Capsule", "60 Nos", 300, "Capsules", "Nos"),
    ("Stoma Fine Capsule", "30 Nos", 190, "Capsules", "Nos"),
    ("Stoma Fine Powder", "100 gm", 160, "Awaleh/Powder", "gm"),
    ("Stoma Fine Gas O Fast", "60 Nos", 170, "Capsules", "Nos"),
    
    # Hair Care - Kesh Vedika Series
    ("Kesh Vedika Anti Hair Lose Capsule", "30 Nos", 410, "Capsules", "Nos"),
    ("Kesh Vedika Hair Oil", "100 ml", 240, "Oils", "ml"),
    ("Kesh Vedika Hair Tonic", "50 ml", 260, "Tonic", "ml"),
    ("Kesh Vedika Hair Wash Powder", "150 gm", 320, "Awaleh/Powder", "gm"),
    ("Kesh Vedika Hair Growth Serum", "50 ml", 480, "Serum", "ml"),
    
    # Energy & Vitality
    ("Shakti Wardaan Gold Plus Capsule", "30 Nos", 690, "Capsules", "Nos"),
    ("Shakti Wardaan 3XSplAwaleh", "250 gm", 1230, "Awaleh/Powder", "gm"),
    ("Shakti Wardaan 3XSplAwaleh", "125 gm", 640, "Awaleh/Powder", "gm"),
    ("Time O Maxx Capsule", "30 Nos", 620, "Capsules", "Nos"),
    ("Paurush Shakti Awaleh", "250 gm", 760, "Awaleh/Powder", "gm"),
    ("Play Maxx Gold Capsule", "10 Nos", 530, "Capsules", "Nos"),
    ("Play Maxx Oil", "15 ml", 230, "Oils", "ml"),
    ("Neframed Capsule", "60 Nos", 890, "Capsules", "Nos"),
    ("Azicool Capsule", "30 Nos", 240, "Capsules", "Nos"),
    
    # Herbal Supplements
    ("Aloe Vera Capsule", "30 Nos", 230, "Capsules", "Nos"),
    ("Amla Capsule", "30 Nos", 230, "Capsules", "Nos"),
    ("Spirulina Capsule", "30 Nos", 330, "Capsules", "Nos"),
    ("Wheatgrass Capsule", "30 Nos", 280, "Capsules", "Nos"),
    ("Punarnava Capsule", "30 Nos", 280, "Capsules", "Nos"),
    ("Ashwagandha Capsule", "30 Nos", 240, "Capsules", "Nos"),
    ("Tulsi Capsule", "30 Nos", 220, "Capsules", "Nos"),
    ("Neem Capsule", "30 Nos", 220, "Capsules", "Nos"),
    ("Giloy Capsule", "30 Nos", 220, "Capsules", "Nos"),
    ("Revivomaxx Capsule", "30 Nos", 650, "Capsules", "Nos"),
    ("Rejuvifyl Capsule", "30 Nos", 650, "Capsules", "Nos"),
    
    # Specialized Products
    ("Man O Maxx Capsule", "30 Nos", 1060, "Capsules", "Nos"),
    ("Pleasure Plus XXX Capsule", "10 Nos", 1100, "Capsules", "Nos"),
    ("Femalotone Capsule", "30 Nos", 790, "Capsules", "Nos"),
    ("Femalotone Syrup", "300 ml", 430, "Syrup", "ml"),
    ("Femalotone Awaleh", "250 gm", 670, "Awaleh/Powder", "gm"),
    ("Hepamed Capsule", "30 Nos", 610, "Capsules", "Nos"),
    ("Neurolaxx Capsule", "30 Nos", 390, "Capsules", "Nos"),
    ("Neurolaxx Capsule", "60 Nos", 750, "Capsules", "Nos"),
    ("Relaxiwave Capsule", "30 Nos", 380, "Capsules", "Nos"),
    ("Relaxiwave Awaleh", "250 gm", 460, "Awaleh/Powder", "gm"),
    ("Cramps Nil Capsule", "30 Nos", 430, "Capsules", "Nos"),
    ("Detoxima Capsule", "30 Nos", 320, "Capsules", "Nos"),
    ("Manjestro Capsule", "30 Nos", 320, "Capsules", "Nos"),
    ("Nezora Capsule", "30 Nos", 340, "Capsules", "Nos"),
    ("Cystocare Capsule", "30 Nos", 460, "Capsules", "Nos"),
    ("Uterexne Capsule", "30 Nos", 820, "Capsules", "Nos"),
    ("Urinexa Capsule", "30 Nos", 340, "Capsules", "Nos"),
    ("Thyrelle Capsule", "30 Nos", 290, "Capsules", "Nos"),
    ("Uresdi Capsule", "30 Nos", 260, "Capsules", "Nos"),
    
    # Honey
    ("Natural Honey", "1 kg", 460, "Honey", "kg"),
    ("Natural Honey", "500 gm", 240, "Honey", "gm"),
    ("Natural Honey", "250 gm", 130, "Honey", "gm"),
    ("Natural Honey", "100 gm", 68, "Honey", "gm"),
]

def import_products():
    """Import all products into the database"""
    print("="*60)
    print("NATURAL HEALTH WORLD - PRODUCT IMPORT")
    print("="*60)
    print(f"Total products to import: {len(PRODUCTS)}")
    print()
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for idx, (name, package_size, mrp, category, unit) in enumerate(PRODUCTS, 1):
        # Create full product name with package size
        full_name = f"{name} {package_size}"
        
        # Check if product already exists
        existing = db.search_products(full_name)
        if existing:
            print(f"[{idx:2d}] SKIP: {full_name} (already exists)")
            skipped_count += 1
            continue
        
        # Calculate selling price with 55% discount
        discount_percent = 55.0
        selling_price = mrp * (1 - discount_percent / 100)
        
        # Prepare product data
        product_data = {
            'name': full_name,
            'category': category,
            'hsn_code': '30049012',
            'unit': unit,
            'package_size': package_size,
            'mrp': mrp,
            'discount_percent': discount_percent,
            'selling_price': selling_price,
            'purchase_price': 0.0,
            'gst_rate': 12.0,
            'current_stock': 0,
            'min_stock_level': 10,
            'barcode': None,
            'description': f"{name} - {package_size}"
        }
        
        # Add product
        try:
            product_id = db.add_product(product_data)
            if product_id:
                print(f"[{idx:2d}] ✓ Added: {full_name} - MRP: ₹{mrp} → Rate: ₹{selling_price:.2f}")
                success_count += 1
            else:
                print(f"[{idx:2d}] ✗ Failed: {full_name}")
                error_count += 1
        except Exception as e:
            print(f"[{idx:2d}] ✗ Error: {full_name} - {str(e)}")
            error_count += 1
    
    print()
    print("="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    print(f"Total products: {len(PRODUCTS)}")
    print(f"Successfully imported: {success_count}")
    print(f"Skipped (already exists): {skipped_count}")
    print(f"Errors: {error_count}")
    print("="*60)
    
    if success_count > 0:
        print()
        print("✓ Products imported successfully!")
        print("  You can now use these products in the billing system.")
    
    return success_count, error_count, skipped_count

if __name__ == "__main__":
    try:
        import_products()
    except Exception as e:
        print(f"\n✗ Import failed with error: {e}")
        import traceback
        traceback.print_exc()
