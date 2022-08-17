import binascii
import os
import re
import requests

import json
#import sys
import shopify
from bs4 import BeautifulSoup
import requests
import pdfplumber
#import PyPDF2
import csv
#import time
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar

class Product:
    productName = "null"
    productDescription = "null"
    salePrice = 0.0
    productCost = 0.0
    SKU = "null"
    sizeRun = list()
    sizeQuantity = list()
    barCodeArray = list()
    productType = "null"
    productVendor = "null"
    collection = "null"
    productTags = "null"
    channels = 0;
    status = "null"
    imageList = list()
    handle = ""
def create_shopify_session():
    shopify.Session.setup(api_key=os.environ['APIKEY'], secret=os.environ['SECRET'])
    shop_url = "invoiceblastfinal.myshopify.com"
    access_token = os.environ['ACCESSTOKEN']
    api_version = '2021-10'
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    redirect_uri = "http://myapp.com/auth/shopify/callback"
    scopes = ['read_products', 'read_orders']
    newSession = shopify.Session(shop_url, api_version)
    auth_url = newSession.create_permission_url(scopes, redirect_uri, state)
    session = shopify.Session(shop_url, api_version)
    session = shopify.Session(shop_url, api_version, access_token)
    shopify.ShopifyResource.activate_session(session)
def FIND_LENGTH(fileName):
    with pdfplumber.open(fileName) as pdf:
        text = ""
        count = 0;
        while count < len(pdf.pages):
            page = pdf.pages[count]
            text += page.extract_text()
            count += 1
        return text.count('Subtotal:')
def RVCA_TO_PRODUCT(fileName, productIndex):
    secretColorCode = ""
    #print("Reading File...")
    returnProduct = Product()
    with pdfplumber.open(fileName) as pdf:
        text = ""
        count = 0;
        while count < len(pdf.pages):
            page = pdf.pages[count]
            text += page.extract_text()
            count += 1
        newChunk = ""
        new_vend_re = re.compile(r'\d{12} .')
        for line in text.split('\n'):
            if new_vend_re.search(line):
                # print(line)W
                newChunk += ("\n" + line)
        # gets chunk of text containing all upcs/sizes
        upcREGEX = re.compile(r'\d{12}')
        upcSIZEREGEX = re.compile(r'\d{12} \w{0,3} \w{0,3}')
        quantREGEX = re.compile(r'\d{1} [EA]')
        skuREGEX = re.compile(r'Subtotal')


        # print(newChunk)

        # create chunk of text by index and only search that chunk
        indexChunk = ""
        index = productIndex
        count = 0
        foundLine = False
        for line in text.split('\n'):
            if foundLine == True and not skuREGEX.findall(line):
                indexChunk += ("\n" + line)
            if foundLine == True and skuREGEX.findall(line):
                break
            if skuREGEX.findall(line) and count == index and foundLine == False:
                # print("function works")
                # print(line)
                indexChunk += ("\n" + line)
                foundLine = True

            if count != index and skuREGEX.findall(line) and foundLine == False:
                count += 1

    #print(upcREGEX.findall(indexChunk))
    #print(quantREGEX.findall(indexChunk))
    upcSizeList = upcSIZEREGEX.findall(indexChunk)
    if upcSizeList == []:
        #find alternative size run find method
        upcSizeList = upcREGEX.findall(indexChunk)
    quantityList = quantREGEX.findall(indexChunk)

    new_quantityList = []
    for index in quantityList:
        new_index = index[0]
        new_quantityList.append(new_index)
        #print(index)
    quantityList = new_quantityList


    new_UPC = []
    new_Size = []
    for index in upcSizeList:
        UPC = index[0:12]
        Size = index[12:]
        new_UPC.append(UPC)
        new_Size.append(Size)

    #print(upcREGEX.findall(indexChunk)[0])
    link = "http://rvca.com/" + upcREGEX.findall(indexChunk)[0][0:12] + ".html"
    #print(link)

    ##site query stuff

    site = requests.get(link).text
    soup = BeautifulSoup(site, 'html.parser')
    # print(soup.prettify())
    name = soup.find(class_="productname").get_text(separator=" ")
    name = name.strip()
    price = soup.find(class_="salesprice").get_text(separator=" ")
    price = price.strip()
    returnProduct.productCost = price
    ##TAG FINDER BELOW
    site = requests.get(link).text
    utagData = (site[site.find("utag_core_data"): site.find("var htag_data")])
    layer2 = utagData[utagData.find("page_categories"): utagData.find("page_en_site_section")]
    bracketData = layer2[layer2.find("["): layer2.find("]")] + "]"
    tagArray = json.loads(bracketData)
    tagArray.pop(0)
    tagArray.pop(0)
    taglist = ""
    for item in tagArray:
        taglist = taglist + item + ", "
    taglist = taglist[:-2]
    productType1 = "accessories"
    # returnproduct.tags = taglist
    if (taglist.find("short") != -1 and taglist.find("shirt") == -1):
        taglist = taglist + "shorts, RVCA shorts"
        productType1 = "bottoms"
    if (taglist.find("shirt") != -1):
        taglist = taglist + ", tees, shirts, RVCA tees"
        productType1 = "shirts"
    ##TAG FINDING COMPLETE

    try:
        color = soup.find(class_="attrTitle").get_text(separator=" ")
        color = color.replace("Color:", "")
        color = color.strip()
        returnProduct.productName = name + " - " + color
        returnProduct.handle = name + " - " + color
    except:
        returnProduct.productName = name
        returnProduct.handle = name.replace(" ","-")


    desc = soup.find(class_="pdp-desc-long").get_text(separator=" ")
    desc = desc.strip()
    returnProduct.productDescription = desc
    sku = soup.find(class_="pdp-desc-block-title-sku").get_text(separator=" ")
    sku = sku.strip()
    returnProduct.SKU = sku
    # gets links to images from source and sizes/ this is where code gets kind of iffy
    rawSources = list()
    sourceList = list()
    substring = "/hi-res/"
    for a in soup.find_all("picture"):
        if a.source:
            rawSources.append(a.source['srcset'])
    sizeList = list()
    for source in rawSources:
        if substring in source:
            sourceList.append(source)
    if sourceList == []:
        mydivs = soup.find_all("a", {"class": "main-image"})
        for source in mydivs:
            sourceList.append(source['href'])
    sizeList = list()
    for a in soup.find_all(class_="swatchanchor obflk ajaxlk href-js"):
        sizeList.append(a)
    #print("sources found")
    status = "draft"
    brand = "RVCA"
    tags = "tagging indeterminate"
    returnProduct.productTags = taglist
    returnProduct.productType = productType1
    returnProduct.sizeRun = new_Size
    returnProduct.imageList = sourceList
    #print(name)
    #print(color)
    #print(price)
    #print(sku)
    #print(desc)
    #print(quantityList)
    #print(new_Size)
    #print(new_UPC)
    #print(sourceList)
    #print(status)
    #print(brand)
    #print(tags)
    #print((float(price[1:]) / 2))


    if new_Size == ['   ']:
        new_Size[0] = ('OS')

    returnProduct.productDescription = desc
    returnProduct.salePrice = price
    returnProduct.productCost = float(price[1:]) / 2
    returnProduct.SKU = sku
    returnProduct.sizeRun = new_Size
    returnProduct.sizeQuantity = quantityList
    returnProduct.barCodeArray = new_UPC
    returnProduct.productType = "null"
    returnProduct.productVendor = "RVCA"
    returnProduct.collection = "null"
    returnProduct.channels = 0;
    returnProduct.status = "draft"
    returnProduct.imageList = sourceList
    #print("File Loaded!")
    #print(taglist)
    return returnProduct
def PRODUCT_TO_CSV(product, file, first):
    #print("writing to csv...")
    while len(product.imageList) < len(product.barCodeArray):
        product.imageList.append('')

    numberArray = list();
    for i in product.imageList:
        numberArray.append(product.imageList.index(i) + 1)
    numberArray.pop()
    while len(numberArray) < len(product.imageList):
        numberArray.append('')

    with open(file, 'a', newline='') as f:
        theWriter = csv.writer(f)
        if first == True:
            theWriter.writerow(['Handle','Title', 'Body (HTML)', 'Vendor','Option1 Name', 'Option1 Value', 'Variant SKU','Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Price', 'Variant Barcode', 'Image Src', 'Image Position','Status'])
        theWriter.writerow([product.handle,product.productName, product.productDescription, product.productVendor, 'Size', product.sizeRun[0], product.SKU,'shopify', product.sizeQuantity[0], product.salePrice, product.barCodeArray[0], product.imageList[0], '1', product.status])
        index = len(product.barCodeArray)
        i = 1
        while i<index:
            theWriter.writerow([product.productName,'', '', '', '', product.sizeRun[i], product.SKU,'shopify', product.sizeQuantity[i], product.salePrice, product.barCodeArray[i], product.imageList[i], numberArray[i], ''])
            i += 1
    #print("product blasted!")
def PRODUCT_TO_SHOPIFY_SESSION(product):
    #print("adding directly to store")
    create_shopify_session()
    new_product = shopify.Product()
    new_product.title = product.productName
    new_product.body_html = product.productDescription
    new_product.tags = product.productTags
    new_product.vendor = "RVCA"
    new_product.collections = product.productType
    new_product.product_type = product.productType

    #image handler
    newImageArray = []
    count = 1
    for image in product.imageList:
        newImageArray.append({'src': '%s' % image, 'position': '%s' % count})
        count += 1
    new_product.images = newImageArray
    #image handling complete

    ### THIS BIT IS UNDER CONSTRUCTION LOGIC NOT WORKING
    new_product.options = [{"name": "Size", "values": product.sizeRun}]
    productVariants = []
    count = 0
    for size in product.sizeRun:
        newVariant = (shopify.Variant({"title": "v" + str(0 + 1), "option1": product.sizeRun[count], "price": product.salePrice, "barcode": product.barCodeArray[count], "sku": product.SKU, "taxable": "true", "inventory_management": "shopify", "cost": (product.salePrice), "inventory_quantity": product.sizeQuantity[count], "position": count + 1}))
        productVariants.append(newVariant)
        count += 1
    #THIS WORKS VERY IMPORTANT PLEASE DO NOT FORGET THIS
    #print(requests.get("https://invoiceblastfinal.myshopify.com/admin/api/2022-07/products/7175551156407/variants/41342351802551.json", headers={'X-Shopify-Access-Token': os.environ['ACCESSTOKEN']}).text)
    new_product.variants = productVariants
    new_product.save()
    count = 0
    for size in product.sizeRun:
        # find variant id
        #find product ID
        productID = str(new_product.attributes['id'])
        variantID = str(new_product.variants[count].attributes['id'])
        #print(productID)
        #print(variantID)
        queryURL = "https://invoiceblastfinal.myshopify.com/admin/api/2022-07/products/" + productID + "/variants/" + variantID + ".json"
        response1 = (requests.get(queryURL, params="inventory_item_id", headers={'X-Shopify-Access-Token': os.environ['ACCESSTOKEN']}))
        jsonData = json.loads(response1.text)
        inventoryItemId = (str(jsonData["variant"]['inventory_item_id']))
        # find location id
        locationURL = "https://invoiceblastfinal.myshopify.com/admin/api/2022-07/inventory_levels.json?inventory_item_ids=" + inventoryItemId
        response2 = (requests.get(locationURL, params="inventory_item_id", headers={'X-Shopify-Access-Token': os.environ['ACCESSTOKEN']}))
        jsonData2 = json.loads(response2.text)
        locationID = (str(jsonData2["inventory_levels"][0]["location_id"]))

        postURL = "https://invoiceblastfinal.myshopify.com/admin/api/2022-07/inventory_levels/adjust.json"
        requests.post(postURL, params={"location_id": locationID, "inventory_item_id": inventoryItemId, "available_adjustment": product.sizeQuantity[count]}, headers={'X-Shopify-Access-Token': os.environ['ACCESSTOKEN']}).text
        count += 1
    success = new_product.save()
def RUN_BLASTER(file, writeFile):
    print("running blaster")
    count = 0;
    percent = 0;
    total = FIND_LENGTH(file)
    inc = 100/total
    while count < FIND_LENGTH(file):
        sampleProduct = RVCA_TO_PRODUCT(file, count)
        if count == 0:
            #PRODUCT_TO_CSV(sampleProduct, writeFile, True)
            PRODUCT_TO_SHOPIFY_SESSION(sampleProduct)
            print("product " + str(count + 1) + " loaded")
        if count != 0:
            #PRODUCT_TO_CSV(sampleProduct, writeFile, False)
            PRODUCT_TO_SHOPIFY_SESSION(sampleProduct)
            print("product " + str(count + 1) + " loaded")
        count += 1
    #print("invoice completed in " + str(round(float(time.time() - start_time), 2)) + " seconds runtime")

filepath = "RVCA6.pdf"
RUN_BLASTER(filepath, 'importFile.csv')





##OBJECTIVES##

#1 store api information in .env files for git pushes
#2 configure variants in product to shopify session
#3 adapt system to make it versatile (i.e. take in arguments for what type of brand/invoice etc rather than assuming RVCA
#4 implement simple UI with fileselect and home screen
#5 support for other brands
#6 optimization/ streamlined error handling/move to map based data transfer for invoice metadata

