# InvoiceLogger1
Web scraper and data formatting system using ShopifyAPI

- - - - - - - - - - - - - - - - 
InvoiceLogger1 Project Overview
- - - - - - - - - - - - - - - -

I initially built the invoice logger to assist me at my own job with the monotonous task of adapting raw product data (in the form of invoices), to shopify product listings

The logger implements a pretty basic pdf reader and web scraper to gather product data (from the pdf invoices and retailer websites for images etc.)
Once it has gathered this data, it formats it into a product class and creates a product listing using the ShopifyAPI

This is a project I intend to improve greatly, some of my goals for the project are the following:

#1 configure variants in product to shopify session
#2 adapt system to make it versatile (i.e. take in arguments for what type of brand/invoice etc rather than assuming RVCA
#3 implement simple UI with fileselect and home screen
#4 support for other brands
#5 optimization/ streamlined error handling/move to map based data transfer for invoice metadata

Cheers,
Hudson
