-- Create the customers table
CREATE TABLE purchase_supp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    PO_Date DATE,
    PO_No VARCHAR(255) NOT NULL,
    supplier_name VARCHAR(255) NOT NULL,
    supplier_contact VARCHAR(255) NOT NULL,


   
    Total_PO_Value VARCHAR(255) NOT NULL,
    No_of_Items_in_PO VARCHAR(20) NOT NULL,
    PO_Delivery_Date Date,
    Employee_Name VARCHAR(255),
    Attachment VARCHAR(255),
    PO_Remarks VARCHAR(255),
    PO_Notes VARCHAR(255),
    total_remarks VARCHAR(255)

);

-- Create the contacts table
CREATE TABLE purchase_supp_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    part_no VARCHAR(255) NOT NULL,
    MFR VARCHAR(20) NOT NULL,
    item_Qty VARCHAR(255) NOT NULL,
    dbc VARCHAR(255),
    part_cost VARCHAR(20),
    item_ext VARCHAR(255),
    PO_ship_Qty VARCHAR(255),
    PO_Item_Delivery_Date VARCHAR(255),
    Freight_Charges VARCHAR(20) NOT NULL,
    Other_Charges VARCHAR(255) NOT NULL,
    Item_Status VARCHAR(255),
   
    FOREIGN KEY (item_id) REFERENCES purchase_supp(id) ON DELETE CASCADE
);
-- Create the manufacturer_product table with an id column
CREATE TABLE manufacturer_product (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Added ID column as the primary key
    manufacturer_name VARCHAR(255),
    remarks TEXT,
    applications TEXT,
    INDEX (manufacturer_name)
);

-- Create the manufacturer_product_stock table
CREATE TABLE manufacturer_product_stock (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_name VARCHAR(255),
    product_name VARCHAR(255) NOT NULL,
    added_by VARCHAR(255),
    remarks TEXT,
    date DATE,
    FOREIGN KEY (manufacturer_name) REFERENCES manufacturer_product(manufacturer_name) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE supplier_offers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    suppliername VARCHAR(255),
    remarks TEXT,
    comments TEXT,
    INDEX (suppliername)  -- Index for faster lookups on suppliername
);
CREATE TABLE add_item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    suppliername VARCHAR(255),
    manufacturer_part_no VARCHAR(255),
    description TEXT,
    manufacturer VARCHAR(255),
    quantity INT,
    date DATE,
    FOREIGN KEY (suppliername) REFERENCES supplier_offers(suppliername) ON DELETE CASCADE ON UPDATE CASCADE
);