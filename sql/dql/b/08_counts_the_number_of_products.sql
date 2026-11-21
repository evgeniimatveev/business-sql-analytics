-- **Product Count by Category** - Counts the number of products in each category.
    
    SELECT category, COUNT(*) AS product_count
    FROM products
    GROUP BY category
    ORDER BY product_count DESC;
-- (fixed: removed a stray markdown code fence that was left at the end of this file)
