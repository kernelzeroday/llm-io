CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    salary INTEGER,
    hire_date DATE
);

INSERT INTO employees (name, department, salary, hire_date) VALUES
('Alice Johnson', 'Engineering', 95000, '2022-01-15'),
('Bob Smith', 'Marketing', 65000, '2021-06-20'),
('Carol Davis', 'Engineering', 105000, '2020-03-10'),
('David Wilson', 'Sales', 75000, '2023-02-28'),
('Eve Brown', 'Engineering', 88000, '2022-11-05'),
('Frank Miller', 'Marketing', 58000, '2023-01-12');

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    budget INTEGER,
    status TEXT
);

INSERT INTO projects (name, department, budget, status) VALUES
('Website Redesign', 'Marketing', 50000, 'Active'),
('Mobile App', 'Engineering', 150000, 'Active'),
('Data Analytics', 'Engineering', 80000, 'Completed'),
('Sales Campaign', 'Sales', 25000, 'Planning'); 