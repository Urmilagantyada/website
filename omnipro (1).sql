-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Sep 13, 2024 at 07:12 AM
-- Server version: 10.1.10-MariaDB
-- PHP Version: 5.5.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `omnipro`
--

-- --------------------------------------------------------

--
-- Table structure for table `add_item`
--

CREATE TABLE `add_item` (
  `id` int(11) NOT NULL,
  `supplier_id` int(11) NOT NULL,
  `manufacturer_part_no` varchar(20) NOT NULL,
  `description` varchar(255) NOT NULL,
  `manufacturer` varchar(255) NOT NULL,
  `quantity` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `add_item`
--

INSERT INTO `add_item` (`id`, `supplier_id`, `manufacturer_part_no`, `description`, `manufacturer`, `quantity`, `date`) VALUES
(1, 5, '123', 'batteries', 'ram', '10', '2024-08-01'),
(2, 6, '11', 'nice', 'rams', '100', '2024-08-01'),
(3, 7, '100', 'top', 'jack', '80', '2024-08-01'),
(4, 8, '13', 'ss', 'ser', '122', '2024-09-04'),
(5, 9, '33', 'ss', 'ee', '23', '2024-09-04'),
(6, 10, '12', 'top', 'wd', '23', '2024-08-01'),
(20, 24, 'sss', 'sss', 'sss', '78', '2024-08-28'),
(21, 25, '11', 'batteries', 'ee', '100', '2024-08-02'),
(22, 26, '656', 'top', 'ram', '23', '2024-08-01'),
(23, 26, '768', 'yup', 'opp', '90', '2024-08-02'),
(24, 27, '33', 'sd', 'ser', '10', '2024-08-22'),
(25, 28, '12', 'batteries', 'ram', '10', '2024-08-02'),
(26, 29, '123', '12', '22', '12', '2024-09-05'),
(27, 30, '123', '2221', 'rams', '456', '2024-08-02'),
(28, 31, '234', 'nice', 'eredds', '10', '2024-08-07'),
(29, 32, '564', 'des', 'tom', '80', '2024-08-29'),
(30, 33, '123', 'top', 'ser', '10', '2024-08-09'),
(31, 34, '090', 'kook', 'sed', '50', '2024-08-02'),
(32, 34, '1', 'hi', 'dsp', 'nicccccc', '2154-06-18'),
(33, 34, '2', 'hiii', 'abc', 'gud', '2154-06-19'),
(34, 34, '3', 'hi', 'abc', 'gud', '2154-06-20'),
(35, 34, '4', 'hiii', 'abc', 'gud', '2154-06-21'),
(36, 34, '5', 'hi', 'abc', 'gud', '2154-06-22'),
(37, 34, '6', 'hiii', 'abc', 'gud', '2154-06-23'),
(38, 34, '7', 'hi', 'abc', 'gud', '2154-06-24'),
(39, 35, '123', '2221', 'ser', '10', '2024-08-09'),
(40, 35, '1', 'hi', 'dsp', 'nicccccc', '2154-06-18'),
(41, 35, '2', 'hiii', 'abc', 'gud', '2154-06-19'),
(42, 35, '3', 'hi', 'abc', 'gud', '2154-06-20'),
(43, 35, '4', 'hiii', 'abc', 'gud', '2154-06-21'),
(44, 35, '5', 'hi', 'abc', 'gud', '2154-06-22'),
(45, 35, '6', 'hiii', 'abc', 'gud', '2154-06-23'),
(46, 35, '7', 'hi', 'abc', 'gud', '2154-06-24');

-- --------------------------------------------------------

--
-- Table structure for table `branch`
--

CREATE TABLE `branch` (
  `id` int(11) NOT NULL,
  `branch_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `branch`
--

INSERT INTO `branch` (`id`, `branch_name`) VALUES
(105, 'MUMABI'),
(104, 'VIZAG');

-- --------------------------------------------------------

--
-- Table structure for table `city`
--

CREATE TABLE `city` (
  `id` int(11) NOT NULL,
  `city` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `city`
--

INSERT INTO `city` (`id`, `city`) VALUES
(24, 'CHENNAI'),
(23, 'HYDERABAD');

-- --------------------------------------------------------

--
-- Table structure for table `contact`
--

CREATE TABLE `contact` (
  `id` int(11) NOT NULL,
  `supplier_name` varchar(255) NOT NULL,
  `contact_person` varchar(255) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `skype` varchar(255) DEFAULT NULL,
  `added_by` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `contact`
--

INSERT INTO `contact` (`id`, `supplier_name`, `contact_person`, `contact_number`, `email`, `skype`, `added_by`) VALUES
(1, 'ROY GROUPS', 'AA', '12233666666', 'raya@gmail.com', '966', 'MAX'),
(4, 'ROY GROUPS', 'ROY', '9347637099', 'a@gmail.com', 's.com', 'JACK'),
(5, 'ROY GROUPS', 'chiru', '9347637099', 'a@gmail.com', 'tom', 'ROSE'),
(6, 'MEERA S', 'RAYA', '12233666666', 's@gmail.com', 'AA', 'JACK'),
(7, 'MEERA S', 'APPLE', '9347637098', 'a@gmail.com', 'hulk', 'JACK'),
(8, 'MEERA S', 'GOOGLE', '9347637099', 'a@gmail.com', 'hulk', 'JACK'),
(9, 'MEERA S', 'ROY', '9347637099', 'a@gmail.com', 'uol', 'KING'),
(10, 'ROY GROUPS', 'MEGA', '9347637099', 'a@gmail.com', 'uol', 'ROSE');

-- --------------------------------------------------------

--
-- Table structure for table `contacts`
--

CREATE TABLE `contacts` (
  `id` int(11) NOT NULL,
  `customer_name` varchar(255) NOT NULL,
  `contact_person` varchar(255) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `department` varchar(255) DEFAULT NULL,
  `whatsapp` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `skype` varchar(255) DEFAULT NULL,
  `added_by` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `contacts`
--

INSERT INTO `contacts` (`id`, `customer_name`, `contact_person`, `contact_number`, `department`, `whatsapp`, `email`, `skype`, `added_by`, `date`) VALUES
(5, 'STEVE', 'BEN', '9490027436', 'MECH', '77777777777', 'a@gmail.com', 'TTT', 'JACKS', '2024-09-12'),
(6, 'STEVE', 'URMILA', '9347963647', 'CSE', '93696541225', 'a@gmail.com', 'uru.com', 'MAX', '2024-08-20'),
(7, 'STEVE', 'ROY', '9347963647', 'CSE', '93696541225', 'a@gmail.com', 'uru.com', 'JACKS', '2024-08-20'),
(8, 'ROSE', 'URMILA', '9347963647', 'CSE', '93696541225', 'a@gmail.com', 'uru.com', 'MAX', '2024-08-20'),
(9, 'ROSE', 'ROY', '9347963647', 'CSE', '93696541225', 'a@gmail.com', 'uru.com', 'ROSE', '2024-08-20'),
(10, 'ROSE', 'MAX', '89098909000', 'MEX', '7896541230', 'luffy@gmail.com', 'POP', 'ROSE', '2024-09-12'),
(13, 'ROSE', 'MEG', '93697456', 'MEX', '7896541230', 'luffy@gmail.com', 'POP', 'ROSE', '2024-09-12'),
(14, 'STEVE', 'RIYA', '89098909000', 'MEX', '7896541230', 'luffy@gmail.com', 'POP', 'ROSE', '2024-09-12'),
(15, 'STEVE', 'PHINS', '89098909000', 'CSE', '7896541230', 'steve@gmail.com', 'POP', 'ROSE', '2024-09-12');

-- --------------------------------------------------------

--
-- Table structure for table `cross_ref`
--

CREATE TABLE `cross_ref` (
  `id` int(11) NOT NULL,
  `man_part_no` varchar(255) NOT NULL,
  `man_name` varchar(255) NOT NULL,
  `cross_part_no` varchar(255) NOT NULL,
  `cross_mfr` varchar(20) NOT NULL,
  `remarks` varchar(20) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `excel` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `id` int(11) NOT NULL,
  `customer_name` varchar(255) NOT NULL,
  `branch` varchar(255) NOT NULL,
  `city` varchar(255) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `contact_fax` varchar(20) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `pincode` int(11) DEFAULT NULL,
  `address` text,
  `customer_profile` text,
  `remarks` text,
  `products` text,
  `applications` text,
  `excel_file` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`id`, `customer_name`, `branch`, `city`, `contact_number`, `contact_fax`, `website`, `pincode`, `address`, `customer_profile`, `remarks`, `products`, `applications`, `excel_file`) VALUES
(2, 'STEVE', 'MUMABI', 'HYDERABAD', '9347637099', '+903788209290-', 'HTTTPS://WWW.OMNIPROSYS.CO', 535547, 'VIZAG', 'GOOD', 'GOOD', 'CHIP', 'LAPTOP', NULL),
(3, 'ROSE', 'MUMABI', 'CHENNAI', '9347637099', '+903788209290-', 'HTTTPS://WWW.OMNIPROSYS.CO', 535545, 'VIZAG', 'GOOD PROFILE', 'GUD', 'BATTERIES', 'LAP', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `customer_invoice`
--

CREATE TABLE `customer_invoice` (
  `id` int(11) NOT NULL,
  `customer_name` varchar(255) NOT NULL,
  `cust_date` date DEFAULT NULL,
  `cust_inv_no` varchar(255) NOT NULL,
  `sales` varchar(255) NOT NULL,
  `pay_terms` varchar(20) NOT NULL,
  `del_terms` varchar(20) NOT NULL,
  `freight` varchar(255) DEFAULT NULL,
  `ship` varchar(255) DEFAULT NULL,
  `bill` varchar(255) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `terms` varchar(255) DEFAULT NULL,
  `NO_items` varchar(255) DEFAULT NULL,
  `inv_value` varchar(255) DEFAULT NULL,
  `attachment` varchar(255) DEFAULT NULL,
  `AWB_attachment` varchar(255) DEFAULT NULL,
  `inv_status` varchar(255) DEFAULT NULL,
  `bank_details` varchar(255) DEFAULT NULL,
  `total_remarks` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `customer_invoice`
--

INSERT INTO `customer_invoice` (`id`, `customer_name`, `cust_date`, `cust_inv_no`, `sales`, `pay_terms`, `del_terms`, `freight`, `ship`, `bill`, `remarks`, `terms`, `NO_items`, `inv_value`, `attachment`, `AWB_attachment`, `inv_status`, `bank_details`, `total_remarks`) VALUES
(1, 'Customername3', '2024-08-09', '303030', 'REP/Sales', 'Paymentterms1', 'Deliveryterms1', 'NoofitemsinP.O1', 'lol', 'l', 'l', 'l', 'NoofitemsinP.O1', 'l', 'customers (17).xls', 'tamra (1).sql', 'Invoicestatus2', 'hook', 'good'),
(2, 'Customername1', '2024-08-25', '2020', 'REP/Sales', 'Paymentterms2', 'Deliveryterms1', 'NoofitemsinP.O2', 'vizag', 'goa', 'good', 'nice', 'NoofitemsinP.O2', '100', 'add-customer.php', 'tamra (1).sql', 'Invoicestatus2', 'BOB', 'good');

-- --------------------------------------------------------

--
-- Table structure for table `customer_invoice_items`
--

CREATE TABLE `customer_invoice_items` (
  `id` int(11) NOT NULL,
  `customer_name` varchar(255) NOT NULL,
  `po_no` varchar(255) NOT NULL,
  `cust_part_no` varchar(20) NOT NULL,
  `mfr_part_no` varchar(255) NOT NULL,
  `manufacturer` varchar(255) DEFAULT NULL,
  `qty` varchar(20) DEFAULT NULL,
  `qty_ship` varchar(20) DEFAULT NULL,
  `qty_bo` varchar(255) DEFAULT NULL,
  `item_price` varchar(255) DEFAULT NULL,
  `item_value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `customer_invoice_items`
--

INSERT INTO `customer_invoice_items` (`id`, `customer_name`, `po_no`, `cust_part_no`, `mfr_part_no`, `manufacturer`, `qty`, `qty_ship`, `qty_bo`, `item_price`, `item_value`) VALUES
(1, 'Customername3', 'P.OPartno40', 'CP.OPartno3', 'MFRPart2', 'MFR2', '20', '20', '20', '20', '200');

-- --------------------------------------------------------

--
-- Table structure for table `deliveryterms`
--

CREATE TABLE `deliveryterms` (
  `id` int(11) NOT NULL,
  `DeliveryTerms` varchar(255) DEFAULT NULL,
  `PaymentTerms` varchar(255) DEFAULT NULL,
  `VIAFreight` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `deliveryterms`
--

INSERT INTO `deliveryterms` (`id`, `DeliveryTerms`, `PaymentTerms`, `VIAFreight`) VALUES
(0, 'jkmgvm', 'kjk', 'nnbn');

-- --------------------------------------------------------

--
-- Table structure for table `designation`
--

CREATE TABLE `designation` (
  `id` int(11) NOT NULL,
  `designation` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `designation`
--

INSERT INTO `designation` (`id`, `designation`, `state`, `city`) VALUES
(1, NULL, NULL, NULL),
(2, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `employee`
--

CREATE TABLE `employee` (
  `id` int(11) NOT NULL,
  `employeename` varchar(255) NOT NULL,
  `joiningdate` date DEFAULT NULL,
  `designation` varchar(255) DEFAULT NULL,
  `dateofbirth` date DEFAULT NULL,
  `bloodgroup` varchar(10) DEFAULT NULL,
  `qualification` varchar(255) DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `address` text,
  `contactnumber` varchar(50) DEFAULT NULL,
  `alternatenumber` varchar(50) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `skype` varchar(255) DEFAULT NULL,
  `remarks` text,
  `updateddate` date DEFAULT NULL,
  `status` tinyint(1) DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `employee`
--

INSERT INTO `employee` (`id`, `employeename`, `joiningdate`, `designation`, `dateofbirth`, `bloodgroup`, `qualification`, `gender`, `address`, `contactnumber`, `alternatenumber`, `city`, `state`, `email`, `skype`, `remarks`, `updateddate`, `status`) VALUES
(5, 'ROSE', '0000-00-00', 'None', '0000-00-00', 'b+', 'ghbjn', 'Gender1', 'jh', '09392371378', 'None', 'city2', 'State1', 'krishnamraju815@gmail.com', 'hjk', '', '2111-02-21', 1),
(6, 'JACKS', '1211-02-11', 'None', '0000-00-00', 'a', '', 'Gender', '', '45121', 'None', 'city1', 'State', '', '', '', '0000-00-00', 0),
(7, 'KING', '2024-08-11', 'Designation2', '2024-08-23', 'B+ve', 'M.Tech', 'Gender2', 'Vizag', '9490027436', '9347637099', 'city3', 'State2', 'steve@gmail.com', 'pop', 'nice', '2024-08-16', 0),
(8, 'MAX', '2024-09-11', 'Designation2', '2024-09-11', 'B+VE', 'M.TECH', 'Gender1', 'VIZAG', '9347637099', '9347637098', 'city2', 'State1', 'tony@gmail.com', 'POP', 'GOOD', '2024-09-28', 1),
(9, 'BENTEN10', '2024-09-13', 'Designation1', '2024-09-07', 'A+VE', 'M.TECH', 'Gender1', 'VIZAG', '9347637099', '1500215', 'city2', 'State1', 'steve@gmail.com', 'S.COM', 'VIZAG', '2024-09-12', 1),
(10, 'KEVIN', '0000-00-00', 'Designation', '0000-00-00', 'AB+VE', '', 'Gender', '', '9347637099', '', 'city1', 'State', '', '', '', '0000-00-00', 0);

-- --------------------------------------------------------

--
-- Table structure for table `expenses`
--

CREATE TABLE `expenses` (
  `id` int(11) NOT NULL,
  `date` date DEFAULT NULL,
  `expensestype` varchar(100) DEFAULT NULL,
  `particulars` varchar(255) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `follow_up`
--

CREATE TABLE `follow_up` (
  `id` int(11) NOT NULL,
  `Issue_Initiated_Date` date DEFAULT NULL,
  `Issue` varchar(255) DEFAULT NULL,
  `Issue_Particulars` text,
  `Issue_Follow_up_Date` date DEFAULT NULL,
  `Update_Information` text,
  `Issue_Status` varchar(255) DEFAULT NULL,
  `Assigned_To` varchar(255) DEFAULT NULL,
  `Assigned_By` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `follow_up`
--

INSERT INTO `follow_up` (`id`, `Issue_Initiated_Date`, `Issue`, `Issue_Particulars`, `Issue_Follow_up_Date`, `Update_Information`, `Issue_Status`, `Assigned_To`, `Assigned_By`) VALUES
(1, '1211-12-12', 'Issue1', 'knk,', '2111-11-13', 'bjb', 'Issue1', 'Assignedto1', 'Assignedby2');

-- --------------------------------------------------------

--
-- Table structure for table `information`
--

CREATE TABLE `information` (
  `id` int(11) NOT NULL,
  `Date` date DEFAULT NULL,
  `Source` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT NULL,
  `Title` varchar(255) DEFAULT NULL,
  `Information` text,
  `Author_Keywords` varchar(255) DEFAULT NULL,
  `Email` varchar(255) DEFAULT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  `Subject` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `information`
--

INSERT INTO `information` (`id`, `Date`, `Source`, `City`, `Title`, `Information`, `Author_Keywords`, `Email`, `Phone`, `Subject`) VALUES
(1, '1211-12-12', 'Source2', 'City2', 'nm', '', '', '', '', 'Subject1');

-- --------------------------------------------------------

--
-- Table structure for table `item`
--

CREATE TABLE `item` (
  `id` int(11) NOT NULL,
  `manufacturername` varchar(255) DEFAULT NULL,
  `distiproposalsent` varchar(100) DEFAULT NULL,
  `updatedate` date DEFAULT NULL,
  `followupdate` date DEFAULT NULL,
  `comments` text,
  `remarks` text,
  `rating` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `item`
--

INSERT INTO `item` (`id`, `manufacturername`, `distiproposalsent`, `updatedate`, `followupdate`, `comments`, `remarks`, `rating`) VALUES
(2, 'manufacturer2', NULL, NULL, '0222-02-12', 'jj', 'hh', NULL),
(3, 'manufacturer1', NULL, NULL, '0000-00-00', 'n', 'kn', NULL),
(4, 'manufacturer3', NULL, NULL, '0000-00-00', 'k', 'l', NULL),
(6, 'manufacturer2', 'yes', '2024-08-21', '2024-08-22', 'GOOD', 'NICE', 5);

-- --------------------------------------------------------

--
-- Table structure for table `managecustomers`
--

CREATE TABLE `managecustomers` (
  `customersid` varchar(255) NOT NULL,
  `customername` varchar(255) DEFAULT NULL,
  `branch` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `contactnumber` varchar(255) DEFAULT NULL,
  `contactfax` varchar(255) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `pincode` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `customerprofile` varchar(255) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `products` varchar(255) DEFAULT NULL,
  `applications` varchar(255) DEFAULT NULL,
  `uploadexcel` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `managestaff`
--

CREATE TABLE `managestaff` (
  `Id` int(11) NOT NULL,
  `StaffId` varchar(20) NOT NULL,
  `StaffName` varchar(255) NOT NULL,
  `StaffRole` varchar(50) NOT NULL,
  `Phone` varchar(15) NOT NULL,
  `Email` varchar(255) NOT NULL,
  `Password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `managestaff`
--

INSERT INTO `managestaff` (`Id`, `StaffId`, `StaffName`, `StaffRole`, `Phone`, `Email`, `Password`) VALUES
(1, 'S001', 'John Doe', 'Reporting Doctor', '1234567890', 'john.doe@example.com', '12345'),
(2, 'S002', 'Jane Smith', 'Referring Doctor', '9876543210', 'jane.smith@example.com', '12345'),
(3, 'S003', 'Alice Johnson', 'Technician', '5551234567', 'alice.johnson@example.com', '12345'),
(4, '2', 'satish', 'Reception', '70360011111', 'satish@gmail.com', '12345'),
(5, '3', 'Aeries', 'admin', '07036001111', 'ramisettychaitanya23@gmail.com', 'admin123'),
(6, '4', 'Harsha', 'Technician', '9142271111', 'harsha@gmail.com', 'password'),
(7, '567', 'Vardhan', 'Referring Doctor', '09142271111', 'test@gmail.com', '12345'),
(8, 'None', 'varshini', 'Technician', '09142271111', 'test@gmail.com', '12345'),
(9, 'None', 'Sandhya', 'Reporting Doctor', '9142271111', 'sandhya@gmail.com', '54321'),
(10, 'None', 'None', 'None', 'None', 'None', 'None'),
(11, 'None', 'None', 'None', 'None', 'None', 'None');

-- --------------------------------------------------------

--
-- Table structure for table `manufacturer_product`
--

CREATE TABLE `manufacturer_product` (
  `id` int(11) NOT NULL,
  `manufacturer_name` varchar(255) DEFAULT NULL,
  `remarks` text,
  `applications` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `manufacturer_product`
--

INSERT INTO `manufacturer_product` (`id`, `manufacturer_name`, `remarks`, `applications`) VALUES
(2, 'Manufacturer3', 'gdf', 'MOBILESsss'),
(3, 'Manufacturer1', 'DF', 'DFG');

-- --------------------------------------------------------

--
-- Table structure for table `manufacturer_product_stock`
--

CREATE TABLE `manufacturer_product_stock` (
  `stock_id` int(11) NOT NULL,
  `manufacturer_name` varchar(255) DEFAULT NULL,
  `product_name` varchar(255) NOT NULL,
  `added_by` varchar(255) DEFAULT NULL,
  `remarks` text,
  `date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `manufacturer_product_stock`
--

INSERT INTO `manufacturer_product_stock` (`stock_id`, `manufacturer_name`, `product_name`, `added_by`, `remarks`, `date`) VALUES
(2, 'Manufacturer1', 'asasd', 'Supplier2', 'nice', '2024-09-12'),
(3, 'Manufacturer1', 'rexss', 'Supplier2', 'WWW', '2024-10-03');

-- --------------------------------------------------------

--
-- Table structure for table `manufacturer_supplier`
--

CREATE TABLE `manufacturer_supplier` (
  `manufacturer_id` int(11) NOT NULL,
  `manufacturer_name` varchar(255) DEFAULT NULL,
  `remarks` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `manufacturer_supplier`
--

INSERT INTO `manufacturer_supplier` (`manufacturer_id`, `manufacturer_name`, `remarks`) VALUES
(1, 'Manufacturer3', 'koko'),
(2, 'Manufacturer3', 'lop');

-- --------------------------------------------------------

--
-- Table structure for table `manufacturer_supplier_stock`
--

CREATE TABLE `manufacturer_supplier_stock` (
  `stock_id` int(11) NOT NULL,
  `manufacturer_name` varchar(255) DEFAULT NULL,
  `supplier_name` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `remarks` text,
  `date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `manufacturer_supplier_stock`
--

INSERT INTO `manufacturer_supplier_stock` (`stock_id`, `manufacturer_name`, `supplier_name`, `type`, `remarks`, `date`) VALUES
(1, 'Manufacturer3', 'raya', 'a@gmail.com', 'huh', '0000-00-00'),
(2, 'Manufacturer3', 'koko', '1@gmail.com', 'huh', '0000-00-00');

-- --------------------------------------------------------

--
-- Table structure for table `opp_rfq`
--

CREATE TABLE `opp_rfq` (
  `id` int(11) NOT NULL,
  `rfq_no` varchar(255) NOT NULL,
  `rfq_date` date DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `customer_name` varchar(255) NOT NULL,
  `end_customer` varchar(255) NOT NULL,
  `project` varchar(20) NOT NULL,
  `application` varchar(20) DEFAULT NULL,
  `assign` varchar(255) DEFAULT NULL,
  `cus_contact` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `opp_rfq`
--

INSERT INTO `opp_rfq` (`id`, `rfq_no`, `rfq_date`, `due_date`, `customer_name`, `end_customer`, `project`, `application`, `assign`, `cus_contact`) VALUES
(1, '123', '2024-08-23', '2024-08-27', 'customer3', 'customer1', 'redd', 'sed', 'Employee3', 'CustomerContact1'),
(2, '123', '2024-08-23', '2024-08-27', 'customer3', 'customer1', 'redd', 'sed', 'Employee3', 'CustomerContact1'),
(3, '123', '2024-08-23', '2024-08-27', 'customer3', 'customer1', 'redd', 'sed', 'Employee3', 'CustomerContact1'),
(4, '123', '2024-08-23', '2024-08-27', 'customer3', 'customer1', 'redd', 'sed', 'Employee3', 'CustomerContact1'),
(5, '678', '2024-08-18', '2024-08-06', 'customer1', 'customer1', 'redd', 'swd', 'Employee1', 'CustomerContact1'),
(6, '1212', '2024-08-01', '2024-08-01', 'customer2', 'customer2', 'aeries', 'nice', 'Employee2', 'CustomerContact1'),
(7, '5236', '2024-09-07', '2024-08-30', 'customer2', 'customer3', 'redd', 'lopkp', 'Employee1', 'CustomerContact1');

-- --------------------------------------------------------

--
-- Table structure for table `opp_rfq_item`
--

CREATE TABLE `opp_rfq_item` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `customer_part_no` varchar(255) NOT NULL,
  `manufacturer_part_no` varchar(20) NOT NULL,
  `manufacturer_name` varchar(255) NOT NULL,
  `req_quantity` varchar(255) DEFAULT NULL,
  `uom` varchar(20) DEFAULT NULL,
  `ext_quantity` varchar(255) DEFAULT NULL,
  `tar_price` varchar(255) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `opp_rfq_item`
--

INSERT INTO `opp_rfq_item` (`id`, `customer_id`, `customer_part_no`, `manufacturer_part_no`, `manufacturer_name`, `req_quantity`, `uom`, `ext_quantity`, `tar_price`, `remarks`) VALUES
(1, 4, '1', '124', '1234', 'ert', '12', '12', '12', 'nice'),
(2, 5, '12', '234', 'wer', '12', '12', '1111', '11', 'nice'),
(3, 6, '12', '100', 'rem', '10', 'gud', '10', '100', 'nice'),
(4, 6, '13', '101', 'ret', '10', 'good', '80', '900', 'nice'),
(5, 7, '202', '630', 'pop', '10', '10', '20', '20', '10');

-- --------------------------------------------------------

--
-- Table structure for table `part_item`
--

CREATE TABLE `part_item` (
  `id` int(11) NOT NULL,
  `man_part_no` varchar(255) NOT NULL,
  `date` varchar(255) NOT NULL,
  `remarks` varchar(255) NOT NULL,
  `excel` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `part_item`
--

INSERT INTO `part_item` (`id`, `man_part_no`, `date`, `remarks`, `excel`) VALUES
(1, '123', '', '', NULL),
(2, '202', '2024-09-01', '45', NULL),
(3, '520', '2024-09-06', 'jok', NULL),
(4, '202', '2024-08-30', 'fhg', NULL),
(5, '12213123', '2024-09-04', 'trt', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `part_number`
--

CREATE TABLE `part_number` (
  `id` int(11) NOT NULL,
  `man_part_no` varchar(255) DEFAULT NULL,
  `part_no` varchar(20) NOT NULL,
  `date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `part_number`
--

INSERT INTO `part_number` (`id`, `man_part_no`, `part_no`, `date`) VALUES
(1, '202', 'Apple', '0000-00-00'),
(2, '202', 'Google', '0000-00-00'),
(3, '202', 'OnePlus', '0000-00-00'),
(4, '202', 'Oppo', '0000-00-00'),
(5, '202', 'Vivo', '0000-00-00'),
(6, '202', 'Xiaomi', '0000-00-00'),
(7, '202', 'Samsung', '0000-00-00'),
(8, '12213123', 'Apple', '0000-00-00'),
(9, '12213123', 'Google', '0000-00-00'),
(10, '12213123', 'OnePlus', '0000-00-00'),
(11, '12213123', 'Oppo', '0000-00-00'),
(12, '12213123', 'Vivo', '0000-00-00'),
(13, '12213123', 'Xiaomi', '0000-00-00'),
(14, '12213123', 'Samsung', '0000-00-00');

-- --------------------------------------------------------

--
-- Table structure for table `product_details`
--

CREATE TABLE `product_details` (
  `id` int(11) NOT NULL,
  `manufacturer_id` int(11) NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `added_by` varchar(255) NOT NULL,
  `date` date NOT NULL,
  `remarks` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `product_details`
--

INSERT INTO `product_details` (`id`, `manufacturer_id`, `product_name`, `added_by`, `date`, `remarks`) VALUES
(1, 15, '77u', 'nn', '2024-07-12', '121@123'),
(2, 16, '77u', 'nn', '0000-00-00', '121@123');

-- --------------------------------------------------------

--
-- Table structure for table `purchase_cus`
--

CREATE TABLE `purchase_cus` (
  `id` int(11) NOT NULL,
  `PO_Date` date DEFAULT NULL,
  `PO_NO` varchar(255) NOT NULL,
  `PO_Recd_Date` date DEFAULT NULL,
  `customer_name` varchar(255) NOT NULL,
  `Total_PO_Value` decimal(10,2) NOT NULL,
  `No_of_Items_in_PO` int(11) NOT NULL,
  `PO_Delivery_Date` date DEFAULT NULL,
  `Employee_Name` varchar(255) DEFAULT NULL,
  `Customer_Contact` varchar(255) DEFAULT NULL,
  `Attachment` varchar(255) DEFAULT NULL,
  `PO_Remarks` varchar(255) DEFAULT NULL,
  `PO_Notes` varchar(255) DEFAULT NULL,
  `total_remarks` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `purchase_cus`
--

INSERT INTO `purchase_cus` (`id`, `PO_Date`, `PO_NO`, `PO_Recd_Date`, `customer_name`, `Total_PO_Value`, `No_of_Items_in_PO`, `PO_Delivery_Date`, `Employee_Name`, `Customer_Contact`, `Attachment`, `PO_Remarks`, `PO_Notes`, `total_remarks`) VALUES
(5, '2024-08-11', '220', '2024-08-23', 'Customername2', '200.00', 2, '2024-08-03', 'Employeename2', 'Customercontact1', NULL, 'loppo', 'lol', '2'),
(6, '2024-08-04', '565', '2024-08-17', 'Customername2', '200.00', 2, '2024-08-04', 'Employeename4', 'Customercontact1', NULL, 'lpop', 'polop', 'good'),
(7, '2024-08-24', '900', '2024-08-23', 'Customername2', '200.00', 1, '2024-08-03', 'Employeename1', 'Customercontact1', NULL, 'lop', 'pol', 'niceee'),
(15, '2024-08-10', '707', '2024-08-02', 'Customername1', '121.00', 1, '2024-08-23', 'Employeename1', 'Customercontact2', NULL, 'hook', 'moon', 'goood'),
(16, '2020-01-08', '2020', '2024-08-23', 'Customername2', '2000.00', 2, '2024-08-16', 'Employeename2', 'Customercontact3', NULL, '', '', ''),
(17, '2024-08-11', '600', '2024-08-09', 'Customername1', '2000.00', 1, '2024-08-08', 'Employeename1', 'Customercontact1', NULL, '', '', ''),
(18, '2024-08-10', '3120', '2024-08-15', 'Customername2', '6000.00', 1, '2024-08-02', 'Employeename2', 'Customercontact1', NULL, '', '', 'koko'),
(21, '2024-08-22', '505', '2024-08-09', 'Customername1', '121.00', 2, '2024-08-04', 'Employeename2', 'Customercontact2', NULL, 'koko', '', ''),
(22, '2024-08-25', '808', '2024-08-31', 'Customername1', '600.00', 1, '2024-08-06', 'Employeename1', 'Customercontact1', NULL, 'good', 'dood', '010'),
(23, '2024-06-10', '202', '2024-09-06', 'Customername3', '121.00', 3, '2024-08-02', 'Employeename2', 'Customercontact1', NULL, 'look', 'pool', 'loop'),
(24, '2024-08-04', '1111', '2024-08-17', 'Customername1', '200.00', 2, '2024-08-02', 'Employeename2', 'Customercontact1', NULL, 'hook', 'hook', '1'),
(25, '2024-08-03', '7070', '2024-08-18', 'Customername1', '2000.00', 2, '2024-08-10', 'Employeename4', 'Customercontact1', NULL, 'sss', 'sss', '02'),
(26, '2024-08-24', '60656', '2024-08-02', 'Customername2', '121.00', 2, '2024-08-13', 'Employeename2', 'Customercontact1', NULL, 'koko', 'ko', ''),
(27, '2024-08-10', '2000', '2024-08-15', 'Customername1', '121.00', 2, '2024-08-17', 'Employeename2', 'Customercontact3', NULL, 'aa', 'ss', 'jooo'),
(28, '2024-08-10', '63022', '2024-08-10', 'Customername1', '121.00', 3, '2024-08-03', 'Employeename2', 'Customercontact1', NULL, 'xxxx', 'aaa', '200'),
(29, '2024-08-17', '9064', '2024-08-18', 'Customername2', '2000.00', 1, '2024-08-02', 'Employeename3', 'Customercontact2', NULL, 'nice', 'nice', 'good'),
(30, '2024-08-18', '456', '2024-08-16', 'Customername1', '300.00', 2, '2024-07-31', 'Employeename2', 'Customercontact2', NULL, '360', 'koko', 'good'),
(31, '2024-08-25', '1020', '2024-08-17', 'Customername3', '2000.00', 1, '2024-08-03', 'Employeename3', 'Customercontact1', 'tamra.sql', 'sert', 'red', '020'),
(32, '2024-08-04', '500', '2024-08-02', 'Customername2', '2020.00', 2, '2024-08-02', 'Employeename1', 'Customercontact1', 'uploads\\customers_17.xls', 'koko', 'jiop', 'hook'),
(33, '2024-08-18', '50510', '2024-08-09', 'Customername3', '100.00', 1, '2024-08-04', 'Employeename2', 'Customercontact1', 'uploads\\contacts_3.xlsx', 'popop', 'lopp', 'koko'),
(34, '2024-08-11', '62222', '2024-08-14', 'Customername2', '0.00', 0, '0000-00-00', '', '', 'uploads\\upload_folder.xlsx', '', '', 'koko'),
(35, '2024-08-17', '901456', '0000-00-00', '', '0.00', 0, '0000-00-00', '', '', NULL, '', '', 'kokoooko'),
(36, '2024-08-10', '10320', '2024-08-16', 'Customername2', '20.00', 2, '2024-08-09', 'Employeename3', 'Customercontact2', 'uploads\\upload_folder.xlsx', '1010', '10', 'gooooood');

-- --------------------------------------------------------

--
-- Table structure for table `purchase_cus_item`
--

CREATE TABLE `purchase_cus_item` (
  `id` int(11) NOT NULL,
  `PO_NO` varchar(255) NOT NULL,
  `part_no` varchar(255) NOT NULL,
  `MFR` varchar(20) NOT NULL,
  `PO_Qty` int(11) NOT NULL,
  `PO_U_P` decimal(10,2) DEFAULT NULL,
  `PO_Item_Value` decimal(10,2) DEFAULT NULL,
  `PO_Ship_Qty` int(11) DEFAULT NULL,
  `PO_Balance_Qty` int(11) DEFAULT NULL,
  `PO_Item_Delivery_Date` date DEFAULT NULL,
  `Freight_Charges` decimal(10,2) DEFAULT NULL,
  `Other_Charges` decimal(10,2) DEFAULT NULL,
  `Item_Status` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `purchase_cus_item`
--

INSERT INTO `purchase_cus_item` (`id`, `PO_NO`, `part_no`, `MFR`, `PO_Qty`, `PO_U_P`, `PO_Item_Value`, `PO_Ship_Qty`, `PO_Balance_Qty`, `PO_Item_Delivery_Date`, `Freight_Charges`, `Other_Charges`, `Item_Status`) VALUES
(1, '900', '2014', '10', 2, '2.00', '2.00', 2, 2, '2024-08-23', '2.00', '2.00', '2'),
(2, '565', '909', '20', 80, '52.00', '2.00', 2, 2, '2024-08-23', '300.00', '300.00', 'nice'),
(3, '900', '20136', '20', 20, '20.00', '2.00', 2, 20, '2024-08-28', '300.00', '300.00', 'nice'),
(4, '900', '20135', '20', 20, '20.00', '2.00', 0, 20, '2024-09-01', '300.00', '2.00', 'nice'),
(5, '707', '2013', '20', 20, '20.00', '2.00', 2, 20, '2024-08-23', '300.00', '300.00', 'nice'),
(6, '2020', '2013', '', 0, '0.00', '0.00', 0, 0, '0000-00-00', '0.00', '0.00', ''),
(7, '3120', '201300', '20', 20, '20.00', '2.00', 2, 20, '2024-08-30', '300.00', '300.00', 'nice'),
(8, '505', '2013', '20', 2, '20.00', '0.00', 0, 0, '0000-00-00', '0.00', '0.00', ''),
(9, '808', '939', '100', 100, '100.00', '100.00', 10, 10, '2024-08-20', '10.00', '1.00', '0'),
(10, '202', '404', '10', 10, '1020.00', '3.00', 20, 2, '2024-09-05', '1000.00', '10.00', '101'),
(11, '1111', '6333', '20', 20, '2.00', '2.00', 0, 1, '0001-01-01', '1.00', '1.00', '1'),
(12, '7070', '2020', '3030', 20, '2.00', '0.00', 20, 2, '2024-08-07', '0.00', '2.00', '0'),
(13, '2000', '3030', '30', 30, '20.00', '20.00', 20, 20, '2024-09-06', '10.00', '0.00', '0'),
(14, '63022', '3030', '30', 3, '0.00', '0.00', 2, 2, '2024-09-06', '2.00', '2.00', '2'),
(15, '9064', '936', '10', 10, '10.00', '10.00', 10, 10, '2024-08-24', '20.00', '20.00', '20'),
(16, '456', '2013', '20', 20, '20.00', '10.00', 10, 10, '2020-01-10', '202.00', '0.00', '1'),
(17, '1020', '909', '202', 2, '0.00', '20.00', 2, 2, '2024-09-06', '20.00', '2.00', '0'),
(18, '1020', '2013', '10', 10, '10.00', '10.00', 101, 10, '2024-09-05', '20.00', '20.00', '20'),
(19, '500', '202', '100', 100, '10.00', '10.00', 10, 10, '2000-02-10', '10.00', '10.00', '10'),
(20, '50510', '30320', '20', 2020, '20.00', '20.00', 20, 20, '2024-08-25', '10.00', '10.00', '10'),
(21, '62222', '1000020', '10', 1, '1.00', '1.00', 1, 1, '2000-01-01', '2.00', '0.00', '2');

-- --------------------------------------------------------

--
-- Table structure for table `purchase_supp`
--

CREATE TABLE `purchase_supp` (
  `id` int(11) NOT NULL,
  `PO_Date` date DEFAULT NULL,
  `PO_NO` varchar(255) NOT NULL,
  `supplier_name` varchar(255) NOT NULL,
  `supplier_contact` varchar(255) NOT NULL,
  `Total_PO_Value` varchar(255) NOT NULL,
  `No_of_Items_in_PO` varchar(20) NOT NULL,
  `PO_Delivery_Date` date DEFAULT NULL,
  `Employee_Name` varchar(255) DEFAULT NULL,
  `Attachment` varchar(255) DEFAULT NULL,
  `PO_Remarks` varchar(255) DEFAULT NULL,
  `PO_Notes` varchar(255) DEFAULT NULL,
  `total_remarks` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `purchase_supp`
--

INSERT INTO `purchase_supp` (`id`, `PO_Date`, `PO_NO`, `supplier_name`, `supplier_contact`, `Total_PO_Value`, `No_of_Items_in_PO`, `PO_Delivery_Date`, `Employee_Name`, `Attachment`, `PO_Remarks`, `PO_Notes`, `total_remarks`) VALUES
(1, '0000-00-00', '', '', '', '', '', '0000-00-00', '', 'calling_data.xls', '', '', ''),
(5, '2024-08-24', '654', 'Supplier2', 'Contact2', '121', '2', '2024-07-31', 'Employee2', 'calling_data.xls', 'koko', 'kok', 'koo'),
(29, '2024-08-24', '505', 'Supplier/Vendor1', 'Supplier/Vendorcontact1', '2000', 'NoofitemsinSP.O2', '2024-08-15', 'Employeename1', 'customers_14.xls', 'koko', 'ko', 'koko'),
(30, '2024-08-18', '6456', 'Supplier/Vendor3', 'Supplier/Vendorcontact2', '100', 'NoofitemsinSP.O1', '2024-08-09', 'Employeename2', 'uploads\\items.xlsx', 'koko', 'kok', 'kkoooo'),
(33, '2024-08-15', '900', 'Supplier/Vendor2', 'Supplier/Vendorcontact2', '6000', 'NoofitemsinSP.O3', '2024-08-02', 'Employeename2', 'calling_data.xls', 'loop', 'loop', 'hokko'),
(34, '0000-00-00', '5555555', 'Supplier/Vendor2', 'Supplier/Vendorcontact3', '6000', 'NoofitemsinSP.O1', '2024-08-16', 'Employeename2', 'calling_data.xls', '5555', '\r\ngtklgk', 'jool'),
(35, '2024-08-10', '20120', 'Supplier/Vendor2', 'Supplier/Vendorcontact1', '200', 'NoofitemsinSP.O2', '2024-07-31', 'Employeename2', 'calling_data.xls', 'koko', 'kok', 'nice'),
(38, '2024-08-10', '2909', 'Supplier/Vendor2', 'Supplier/Vendorcontact1', '200', 'NoofitemsinSP.O2', '2024-07-31', 'Employeename2', 'calling_data.xls', 'koko', 'kok', 'nice'),
(39, '2024-08-18', '963', 'Supplier/Vendor3', 'Supplier/Vendorcontact1', '100', 'NoofitemsinSP.O2', '2024-08-22', 'Employeename2', 'Screenshot_25_1.png', 'koko', 'ko', 'joo'),
(41, '2024-08-18', '963999', 'Supplier/Vendor3', 'Supplier/Vendorcontact1', '100', 'NoofitemsinSP.O2', '2024-08-22', 'Employeename2', 'Screenshot_25_1.png', 'koko', 'ko', 'joo'),
(42, '2024-08-25', '100', 'Supplier/Vendor1', 'Supplier/Vendorcontact2', '20000', 'NoofitemsinSP.O1', '2024-08-24', 'Employeename1', 'tamra.sql', 'good', 'good', 'good'),
(43, '2024-08-31', '90000', 'Supplier/Vendor2', 'Supplier/Vendorcontact2', '2000', 'NoofitemsinSP.O2', '2024-08-08', 'Employeename1', 'calling_data.xls', 'koko', 'ret', 'kok');

-- --------------------------------------------------------

--
-- Table structure for table `purchase_supp_item`
--

CREATE TABLE `purchase_supp_item` (
  `id` int(11) NOT NULL,
  `PO_NO` varchar(255) NOT NULL,
  `part_no` varchar(255) NOT NULL,
  `MFR` varchar(20) NOT NULL,
  `item_Qty` varchar(255) NOT NULL,
  `dbc` varchar(255) DEFAULT NULL,
  `part_cost` varchar(20) DEFAULT NULL,
  `item_ext` varchar(255) DEFAULT NULL,
  `PO_ship_Qty` varchar(255) DEFAULT NULL,
  `Balance_Qty` varchar(100) NOT NULL,
  `PO_Item_Delivery_Date` varchar(255) DEFAULT NULL,
  `Freight_Charges` varchar(20) NOT NULL,
  `Other_Charges` varchar(255) NOT NULL,
  `Item_Status` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `purchase_supp_item`
--

INSERT INTO `purchase_supp_item` (`id`, `PO_NO`, `part_no`, `MFR`, `item_Qty`, `dbc`, `part_cost`, `item_ext`, `PO_ship_Qty`, `Balance_Qty`, `PO_Item_Delivery_Date`, `Freight_Charges`, `Other_Charges`, `Item_Status`) VALUES
(1, '963999', '2013', '', '', '', '', '', '', '', '', '', '', ''),
(2, '100', '1001', '100', '10', '10', '10', '10', '10', '10', '2024-08-07', '2000', '2000', 'nice'),
(3, '100', '1002', '200', '20', '20', '20', '20', '20', '20', '2024-08-25', '2000', '02000', 'nice'),
(4, '90000', '300', '30', '30', '20', '20', '20', '0', '2', '2024-08-06', '100', '100', 'lop');

-- --------------------------------------------------------

--
-- Table structure for table `suppliers`
--

CREATE TABLE `suppliers` (
  `id` int(11) NOT NULL,
  `supplier_name` varchar(255) NOT NULL,
  `sub_type` varchar(255) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `fax` varchar(20) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `address` text,
  `remarks` varchar(255) DEFAULT NULL,
  `applications` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `suppliers`
--

INSERT INTO `suppliers` (`id`, `supplier_name`, `sub_type`, `contact_number`, `fax`, `website`, `address`, `remarks`, `applications`) VALUES
(1, 'ROY GROUPS', 'Manufacturer', '9347637099', '456', 'HTTTPS://WWW.OMNIPROSYS.CO', 'VIZAG', 'GOOD', 'CHIP'),
(2, 'MEERA S', 'Distributor', '9347637099', '789', 'HTTTPS://WWW.OMNIPROSYS.CO', 'VIZAG', 'GOOD', 'BATTERIES');

-- --------------------------------------------------------

--
-- Table structure for table `supplier_invoice`
--

CREATE TABLE `supplier_invoice` (
  `id` int(11) NOT NULL,
  `supplier_name` varchar(255) NOT NULL,
  `supp_date` date DEFAULT NULL,
  `supp_inv_no` varchar(255) NOT NULL,
  `supp_contact` varchar(255) NOT NULL,
  `pay_terms` varchar(20) NOT NULL,
  `del_terms` varchar(20) NOT NULL,
  `freight` varchar(255) DEFAULT NULL,
  `ship` varchar(255) DEFAULT NULL,
  `bill` varchar(255) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `terms` varchar(255) DEFAULT NULL,
  `NO_items` varchar(255) DEFAULT NULL,
  `inv_value` varchar(255) DEFAULT NULL,
  `attachment` varchar(255) DEFAULT NULL,
  `AWB_attachment` varchar(255) DEFAULT NULL,
  `inv_status` varchar(255) DEFAULT NULL,
  `bank_details` varchar(255) DEFAULT NULL,
  `total_remarks` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `supplier_invoice`
--

INSERT INTO `supplier_invoice` (`id`, `supplier_name`, `supp_date`, `supp_inv_no`, `supp_contact`, `pay_terms`, `del_terms`, `freight`, `ship`, `bill`, `remarks`, `terms`, `NO_items`, `inv_value`, `attachment`, `AWB_attachment`, `inv_status`, `bank_details`, `total_remarks`) VALUES
(3, 'Supp/Vendor2', '2024-08-23', '200', 'Supp/Vendorcontact', 'Supp/VendorPaymentte', '', '', 'hook', 'koko', 'ko', 'ko', 'NoofitemsinP.O2', '100', 'brand (9).xlsx', 'brand (9).xlsx', 'Invoicestatus1', 'kokokok', 'None');

-- --------------------------------------------------------

--
-- Table structure for table `supplier_invoice_items`
--

CREATE TABLE `supplier_invoice_items` (
  `id` int(11) NOT NULL,
  `supplier_name` varchar(255) NOT NULL,
  `po_no` varchar(255) NOT NULL,
  `supp_part_no` varchar(20) NOT NULL,
  `mfr_part_no` varchar(255) NOT NULL,
  `manufacturer` varchar(255) DEFAULT NULL,
  `qty` varchar(20) DEFAULT NULL,
  `qty_ship` varchar(20) DEFAULT NULL,
  `qty_bo` varchar(255) DEFAULT NULL,
  `item_price` varchar(255) DEFAULT NULL,
  `item_value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `supplier_invoice_items`
--

INSERT INTO `supplier_invoice_items` (`id`, `supplier_name`, `po_no`, `supp_part_no`, `mfr_part_no`, `manufacturer`, `qty`, `qty_ship`, `qty_bo`, `item_price`, `item_value`) VALUES
(1, 'Supp/Vendor2', 'P.OPartno1', 'CP.OPartno1', 'MFRPart1', 'MFR1', '', '', '', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `supplier_offers`
--

CREATE TABLE `supplier_offers` (
  `id` int(11) NOT NULL,
  `suppliername` varchar(255) NOT NULL,
  `remarks` varchar(255) NOT NULL,
  `comments` varchar(255) NOT NULL,
  `excel` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `supplier_offers`
--

INSERT INTO `supplier_offers` (`id`, `suppliername`, `remarks`, `comments`, `excel`) VALUES
(5, 'suppliername3', 'nice', 'nice', NULL),
(6, 'suppliername3', 'green', 'vgud', NULL),
(7, 'suppliername4', 'wert', 'ss', NULL),
(8, 'suppliername1', 'tpp', 'ss', NULL),
(9, 'suppliername1', 'ss', 'ss', NULL),
(10, 'suppliername2', 'we', 'we', NULL),
(24, 'suppliername2', 'ss', 'sss', NULL),
(25, 'suppliername1', 's', 's', NULL),
(26, 'suppliername4', 'ttt', 'uuu', NULL),
(27, 'suppliername4', 'swwe', 'ss', NULL),
(28, 'suppliername2', 'aa', 'ss', NULL),
(29, 'suppliername1', 'tom', 'yom', NULL),
(30, 'suppliername2', 'ee', 'ee', NULL),
(31, 'suppliername2', 'west', 'red', NULL),
(32, 'suppliername2', 'good', 'nice', NULL),
(33, 'suppliername2', 'sss', 'ssss', NULL),
(34, 'suppliername2', 'ko', 'ok', NULL),
(35, 'suppliername2', 'sed', 'aas', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `supplier_quote`
--

CREATE TABLE `supplier_quote` (
  `id` int(11) NOT NULL,
  `supplier_name` varchar(255) DEFAULT NULL,
  `rfq_date` date DEFAULT NULL,
  `quote_date` date DEFAULT NULL,
  `supplier_contact` varchar(100) DEFAULT NULL,
  `attachment` varchar(255) DEFAULT NULL,
  `remarks` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `supplier_quote`
--

INSERT INTO `supplier_quote` (`id`, `supplier_name`, `rfq_date`, `quote_date`, `supplier_contact`, `attachment`, `remarks`) VALUES
(1, 'Manufacturer3', '2024-08-03', '2024-08-03', '5222', NULL, 'good'),
(2, 'Manufacturer3', '2024-08-03', '2024-08-03', 'Suppliercontact1', NULL, 'good'),
(3, 'Manufacturer3', '2024-08-03', '2024-08-03', 'Suppliercontact1', NULL, 'good'),
(4, 'Manufacturer3', '2024-08-03', '2024-08-03', 'Suppliercontact1', NULL, 'good'),
(5, 'Manufacturer2', '2024-08-03', '2024-08-10', 'Suppliercontact3', NULL, 'jok'),
(6, 'Manufacturer2', '2024-08-03', '2024-08-10', 'Suppliercontact3', NULL, 'jok'),
(7, 'Manufacturer4', '2024-08-03', '2024-08-11', 'Suppliercontact4', 'customers (15).xls', 'ssss'),
(8, 'Manufacturer1', '2024-08-03', '2024-08-10', 'Suppliercontact2', 'items (1).xlsx', 'good'),
(9, 'Manufacturer2', '2024-08-11', '2024-09-02', 'Suppliercontact2', 'book.xlsx', 'nice'),
(10, 'Manufacturer3', '2024-08-17', '2024-08-17', 'Suppliercontact3', 'Screenshot (25) (11).png', '1'),
(11, 'Manufacturer3', '2024-08-30', '2024-08-16', '', 'Harsha-cv.pdf', 'hook'),
(12, 'Manufacturer1', '0000-00-00', '0000-00-00', 'Suppliercontact2', 'background.jpg', '');

-- --------------------------------------------------------

--
-- Table structure for table `supplier_quote_rfq`
--

CREATE TABLE `supplier_quote_rfq` (
  `id` int(11) NOT NULL,
  `supplier_name` varchar(255) DEFAULT NULL,
  `part_no` varchar(255) DEFAULT NULL,
  `make` varchar(255) DEFAULT NULL,
  `stock` varchar(255) DEFAULT NULL,
  `price` varchar(255) DEFAULT NULL,
  `item` varchar(255) DEFAULT NULL,
  `details` text,
  `remarks` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `supplier_quote_rfq`
--

INSERT INTO `supplier_quote_rfq` (`id`, `supplier_name`, `part_no`, `make`, `stock`, `price`, `item`, `details`, `remarks`) VALUES
(1, 'Manufacturer2', '505', 'koko', '100', '1000', '9000', 'NICW', 'NICE'),
(2, 'Manufacturer4', '505', 'KOKO', '100', '1000', '9000', 'NICW', 'WWW'),
(3, 'Manufacturer1', '1010', '2020', '100', '100', '5000', 'SS', 'NICE'),
(4, 'Manufacturer2', '606', '20', '100', '20000', '200', '2000', 'GOOD'),
(5, 'Manufacturer2', '607', '20', '20', '2000', '20', '20', 'NICE'),
(6, 'Manufacturer3', '10', '0', '0', '0', '1', '1', '1'),
(7, 'Manufacturer3', '50', 'KOKO', '100', '1000', '9000', 'SS', 'SSS');

-- --------------------------------------------------------

--
-- Table structure for table `terminology`
--

CREATE TABLE `terminology` (
  `id` int(11) NOT NULL,
  `Date` date DEFAULT NULL,
  `Keyword` varchar(255) DEFAULT NULL,
  `Alphabet` char(1) DEFAULT NULL,
  `Description` text,
  `Remarks` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `terminology`
--

INSERT INTO `terminology` (`id`, `Date`, `Keyword`, `Alphabet`, `Description`, `Remarks`) VALUES
(1, '4544-05-21', 'nkn', 'A', '', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `add_item`
--
ALTER TABLE `add_item`
  ADD PRIMARY KEY (`id`),
  ADD KEY `supplier_id` (`supplier_id`);

--
-- Indexes for table `branch`
--
ALTER TABLE `branch`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branch_name` (`branch_name`);

--
-- Indexes for table `city`
--
ALTER TABLE `city`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `city` (`city`);

--
-- Indexes for table `contact`
--
ALTER TABLE `contact`
  ADD PRIMARY KEY (`id`),
  ADD KEY `supplier_name` (`supplier_name`);

--
-- Indexes for table `contacts`
--
ALTER TABLE `contacts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_name` (`customer_name`);

--
-- Indexes for table `cross_ref`
--
ALTER TABLE `cross_ref`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `customer_name` (`customer_name`);

--
-- Indexes for table `customer_invoice`
--
ALTER TABLE `customer_invoice`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `customer_name` (`customer_name`);

--
-- Indexes for table `customer_invoice_items`
--
ALTER TABLE `customer_invoice_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_name` (`customer_name`);

--
-- Indexes for table `employee`
--
ALTER TABLE `employee`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `item`
--
ALTER TABLE `item`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `manufacturer_product`
--
ALTER TABLE `manufacturer_product`
  ADD PRIMARY KEY (`id`),
  ADD KEY `manufacturer_name` (`manufacturer_name`);

--
-- Indexes for table `manufacturer_product_stock`
--
ALTER TABLE `manufacturer_product_stock`
  ADD PRIMARY KEY (`stock_id`),
  ADD KEY `manufacturer_name` (`manufacturer_name`);

--
-- Indexes for table `manufacturer_supplier`
--
ALTER TABLE `manufacturer_supplier`
  ADD PRIMARY KEY (`manufacturer_id`),
  ADD KEY `manufacturer_name` (`manufacturer_name`);

--
-- Indexes for table `manufacturer_supplier_stock`
--
ALTER TABLE `manufacturer_supplier_stock`
  ADD PRIMARY KEY (`stock_id`),
  ADD KEY `manufacturer_name` (`manufacturer_name`);

--
-- Indexes for table `opp_rfq`
--
ALTER TABLE `opp_rfq`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `opp_rfq_item`
--
ALTER TABLE `opp_rfq_item`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`);

--
-- Indexes for table `part_item`
--
ALTER TABLE `part_item`
  ADD PRIMARY KEY (`id`),
  ADD KEY `man_part_no` (`man_part_no`);

--
-- Indexes for table `part_number`
--
ALTER TABLE `part_number`
  ADD PRIMARY KEY (`id`),
  ADD KEY `man_part_no` (`man_part_no`);

--
-- Indexes for table `purchase_cus`
--
ALTER TABLE `purchase_cus`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `PO_NO` (`PO_NO`);

--
-- Indexes for table `purchase_cus_item`
--
ALTER TABLE `purchase_cus_item`
  ADD PRIMARY KEY (`id`),
  ADD KEY `PO_NO` (`PO_NO`);

--
-- Indexes for table `purchase_supp`
--
ALTER TABLE `purchase_supp`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `PO_NO` (`PO_NO`);

--
-- Indexes for table `purchase_supp_item`
--
ALTER TABLE `purchase_supp_item`
  ADD PRIMARY KEY (`id`),
  ADD KEY `PO_NO` (`PO_NO`);

--
-- Indexes for table `suppliers`
--
ALTER TABLE `suppliers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `supplier_name` (`supplier_name`);

--
-- Indexes for table `supplier_invoice`
--
ALTER TABLE `supplier_invoice`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `supplier_name` (`supplier_name`);

--
-- Indexes for table `supplier_invoice_items`
--
ALTER TABLE `supplier_invoice_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `supplier_name` (`supplier_name`);

--
-- Indexes for table `supplier_offers`
--
ALTER TABLE `supplier_offers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `supplier_quote`
--
ALTER TABLE `supplier_quote`
  ADD PRIMARY KEY (`id`),
  ADD KEY `supplier_name` (`supplier_name`);

--
-- Indexes for table `supplier_quote_rfq`
--
ALTER TABLE `supplier_quote_rfq`
  ADD PRIMARY KEY (`id`),
  ADD KEY `supplier_name` (`supplier_name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `add_item`
--
ALTER TABLE `add_item`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;
--
-- AUTO_INCREMENT for table `branch`
--
ALTER TABLE `branch`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=106;
--
-- AUTO_INCREMENT for table `city`
--
ALTER TABLE `city`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;
--
-- AUTO_INCREMENT for table `contact`
--
ALTER TABLE `contact`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
--
-- AUTO_INCREMENT for table `contacts`
--
ALTER TABLE `contacts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;
--
-- AUTO_INCREMENT for table `cross_ref`
--
ALTER TABLE `cross_ref`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT for table `customer_invoice`
--
ALTER TABLE `customer_invoice`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT for table `customer_invoice_items`
--
ALTER TABLE `customer_invoice_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT for table `employee`
--
ALTER TABLE `employee`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
--
-- AUTO_INCREMENT for table `item`
--
ALTER TABLE `item`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
--
-- AUTO_INCREMENT for table `manufacturer_product`
--
ALTER TABLE `manufacturer_product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT for table `manufacturer_product_stock`
--
ALTER TABLE `manufacturer_product_stock`
  MODIFY `stock_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT for table `manufacturer_supplier`
--
ALTER TABLE `manufacturer_supplier`
  MODIFY `manufacturer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT for table `manufacturer_supplier_stock`
--
ALTER TABLE `manufacturer_supplier_stock`
  MODIFY `stock_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT for table `opp_rfq`
--
ALTER TABLE `opp_rfq`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
--
-- AUTO_INCREMENT for table `opp_rfq_item`
--
ALTER TABLE `opp_rfq_item`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT for table `part_item`
--
ALTER TABLE `part_item`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT for table `part_number`
--
ALTER TABLE `part_number`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;
--
-- AUTO_INCREMENT for table `purchase_cus`
--
ALTER TABLE `purchase_cus`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;
--
-- AUTO_INCREMENT for table `purchase_cus_item`
--
ALTER TABLE `purchase_cus_item`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;
--
-- AUTO_INCREMENT for table `purchase_supp`
--
ALTER TABLE `purchase_supp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=44;
--
-- AUTO_INCREMENT for table `purchase_supp_item`
--
ALTER TABLE `purchase_supp_item`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT for table `suppliers`
--
ALTER TABLE `suppliers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT for table `supplier_invoice`
--
ALTER TABLE `supplier_invoice`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT for table `supplier_invoice_items`
--
ALTER TABLE `supplier_invoice_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT for table `supplier_offers`
--
ALTER TABLE `supplier_offers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;
--
-- AUTO_INCREMENT for table `supplier_quote`
--
ALTER TABLE `supplier_quote`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;
--
-- AUTO_INCREMENT for table `supplier_quote_rfq`
--
ALTER TABLE `supplier_quote_rfq`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `add_item`
--
ALTER TABLE `add_item`
  ADD CONSTRAINT `add_item_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `supplier_offers` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `contact`
--
ALTER TABLE `contact`
  ADD CONSTRAINT `contact_ibfk_1` FOREIGN KEY (`supplier_name`) REFERENCES `suppliers` (`supplier_name`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `contacts`
--
ALTER TABLE `contacts`
  ADD CONSTRAINT `contacts_ibfk_1` FOREIGN KEY (`customer_name`) REFERENCES `customers` (`customer_name`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `customer_invoice_items`
--
ALTER TABLE `customer_invoice_items`
  ADD CONSTRAINT `customer_invoice_items_ibfk_1` FOREIGN KEY (`customer_name`) REFERENCES `customer_invoice` (`customer_name`) ON DELETE CASCADE;

--
-- Constraints for table `manufacturer_product_stock`
--
ALTER TABLE `manufacturer_product_stock`
  ADD CONSTRAINT `manufacturer_product_stock_ibfk_1` FOREIGN KEY (`manufacturer_name`) REFERENCES `manufacturer_product` (`manufacturer_name`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `manufacturer_supplier_stock`
--
ALTER TABLE `manufacturer_supplier_stock`
  ADD CONSTRAINT `manufacturer_supplier_stock_ibfk_1` FOREIGN KEY (`manufacturer_name`) REFERENCES `manufacturer_supplier` (`manufacturer_name`) ON DELETE CASCADE;

--
-- Constraints for table `opp_rfq_item`
--
ALTER TABLE `opp_rfq_item`
  ADD CONSTRAINT `opp_rfq_item_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `opp_rfq` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `part_number`
--
ALTER TABLE `part_number`
  ADD CONSTRAINT `part_number_ibfk_1` FOREIGN KEY (`man_part_no`) REFERENCES `part_item` (`man_part_no`) ON DELETE CASCADE;

--
-- Constraints for table `purchase_cus_item`
--
ALTER TABLE `purchase_cus_item`
  ADD CONSTRAINT `purchase_cus_item_ibfk_1` FOREIGN KEY (`PO_NO`) REFERENCES `purchase_cus` (`PO_NO`) ON DELETE CASCADE;

--
-- Constraints for table `purchase_supp_item`
--
ALTER TABLE `purchase_supp_item`
  ADD CONSTRAINT `purchase_supp_item_ibfk_1` FOREIGN KEY (`PO_NO`) REFERENCES `purchase_supp` (`PO_NO`) ON DELETE CASCADE;

--
-- Constraints for table `supplier_invoice_items`
--
ALTER TABLE `supplier_invoice_items`
  ADD CONSTRAINT `supplier_invoice_items_ibfk_1` FOREIGN KEY (`supplier_name`) REFERENCES `supplier_invoice` (`supplier_name`) ON DELETE CASCADE;

--
-- Constraints for table `supplier_quote_rfq`
--
ALTER TABLE `supplier_quote_rfq`
  ADD CONSTRAINT `supplier_quote_rfq_ibfk_1` FOREIGN KEY (`supplier_name`) REFERENCES `supplier_quote` (`supplier_name`) ON DELETE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
