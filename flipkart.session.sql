-- @block
CREATE TABLE table1 (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product VARCHAR(255) NOT NULL,
    link TEXT NOT NULL,
    price INT NOT NULL
);
-- @block
CREATE TABLE table2 (
    product VARCHAR(255) NOT NULL UNIQUE,
    lowest_price INT NOT NULL,
    rating FLOAT NOT NULL,
    link TEXT NOT NULL
);
-- @block
CREATE TABLE table3 (
    product VARCHAR(255) NOT NULL UNIQUE,
    search_link TEXT NOT NULL
);
-- @block
DROP TABLE table2;

-- @block
SELECT * FROM table1