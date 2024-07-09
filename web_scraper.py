import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL of the e-commerce website
BASE_URL = 'https://books.toscrape.com/catalogue/page-{}.html'

# Initialize an empty list to store product details
products = []

def scrape_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        logging.info('Successfully accessed the website: %s', url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product details
        for product in soup.select('.product_pod'):
            name = product.select_one('h3 > a').attrs['title']
            price = product.select_one('.price_color').text.strip()
            rating = product.select_one('.star-rating').attrs['class'][1]  # e.g., "One", "Two", etc.
            products.append({'Name': name, 'Price': price, 'Rating': rating})
    else:
        logging.error('Failed to access the website. Status code: %s', response.status_code)

# Iterate through the pages
page = 1
while True:
    url = BASE_URL.format(page)
    scrape_page(url)
    
    # Check if there's a "next" button to go to the next page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    if not soup.select_one('.next > a'):
        break  # Exit the loop if there are no more pages
    
    page += 1
    time.sleep(1)  # Be polite and avoid overwhelming the server

# Save data to CSV
df = pd.DataFrame(products)
df.to_csv('products.csv', index=False)
logging.info('Data saved to products.csv')

# Generate HTML file
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scraped Products</title>
    <!-- Bootstrap CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom styles -->
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1 class="mt-4 mb-4">Scraped Products</h1>
        <div class="table-responsive">
            <table class="table table-striped">
                <thead class="thead-dark">
                    <tr>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>
"""

for index, row in df.iterrows():
    html_content += f"""
                    <tr>
                        <td>{row['Name']}</td>
                        <td>{row['Price']}</td>
                        <td>{row['Rating']}</td>
                    </tr>
"""

html_content += """
                </tbody>
            </table>
        </div>
    </div>

    <!-- Bootstrap JS and dependencies (optional, for certain Bootstrap features) -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as file:
    file.write(html_content)
    logging.info('HTML file generated: index.html')
