CREATE DATABASE RFM_Segmentation;
USE RFM_Segmentation;


CREATE VIEW vw_RFM_Base AS
WITH CleanedData AS (
    -- Step 1: Clean the raw data
    -- We must remove rows with no CustomerID, and remove returned items (negative quantities)
    SELECT 
        InvoiceNo,
        StockCode,
        Quantity,
        CAST(InvoiceDate AS DATE) AS InvoiceDate,
        UnitPrice,
        CustomerID,
        (Quantity * UnitPrice) AS TotalSpend
    FROM 
        Online_Retail
    WHERE 
        CustomerID IS NOT NULL 
        AND Quantity > 0 
        AND UnitPrice > 0
),
ReferenceDate AS (
    -- Step 2: Find the "Current Date" of the dataset
    -- Since this data is from 2011, we pretend the "current day" is one day after the last transaction
    SELECT MAX(InvoiceDate) AS MaxDate 
    FROM CleanedData
)
-- Step 3: Calculate the R, F, and M for each unique customer
SELECT 
    c.CustomerID,
    -- Recency: Days between their last purchase and the "Current Date"
    DATEDIFF(day, MAX(c.InvoiceDate), r.MaxDate) AS Recency,
    
    -- Frequency: Count of unique invoices (visits)
    COUNT(DISTINCT c.InvoiceNo) AS Frequency,
    
    -- Monetary: Total money spent across all their invoices
    SUM(c.TotalSpend) AS Monetary
FROM 
    CleanedData c
CROSS JOIN 
    ReferenceDate r
GROUP BY 
    c.CustomerID, r.MaxDate;


    SELECT * FROM vw_RFM_Base;