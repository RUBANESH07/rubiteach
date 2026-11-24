/* Rubitech Academy – SQL playground dataset and badge metadata.
   Courses, modules and lessons come from the API; answers and hints never leave the server. */

window.SEED_SQL = `
CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT NOT NULL, location TEXT);
CREATE TABLE employees (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, department_id INTEGER REFERENCES departments(id),
  job_title TEXT, salary INTEGER, hire_date TEXT, manager_id INTEGER);
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT, country TEXT);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT, price REAL, stock INTEGER);
CREATE TABLE orders (
  id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id),
  product_id INTEGER REFERENCES products(id), quantity INTEGER, order_date TEXT, status TEXT);

INSERT INTO departments VALUES (1,'Engineering','New York'),(2,'Marketing','Chicago'),(3,'Sales','Austin'),(4,'HR','Boston');

INSERT INTO employees VALUES
(1,'Alice Johnson',1,'Engineering Manager',125000,'2018-03-12',NULL),
(2,'Bob Smith',1,'Software Engineer',95000,'2020-06-01',1),
(3,'Carla Gomez',1,'Data Analyst',82000,'2021-01-15',1),
(4,'David Lee',2,'Marketing Lead',88000,'2019-09-23',NULL),
(5,'Emma Brown',2,'Content Writer',56000,'2022-02-14',4),
(6,'Frank Wilson',3,'Sales Director',110000,'2017-11-30',NULL),
(7,'Grace Kim',3,'Sales Executive',64000,'2021-08-09',6),
(8,'Henry Davis',3,'Sales Executive',61000,'2023-01-16',6),
(9,'Isla Martin',4,'HR Manager',78000,'2018-05-07',NULL),
(10,'Jack Turner',1,'Software Engineer',99000,'2019-12-02',1),
(11,'Karen White',2,'SEO Specialist',59000,'2022-10-10',4),
(12,'Liam Clark',3,'Sales Executive',66000,'2020-03-25',6);

INSERT INTO customers VALUES
(1,'Ava Patel','New York','USA'),(2,'Noah Garcia','Madrid','Spain'),(3,'Mia Rossi','Rome','Italy'),
(4,'Leo Dubois','Paris','France'),(5,'Zoe Chen','Singapore','Singapore'),(6,'Omar Hassan','Cairo','Egypt'),
(7,'Ella Novak','Prague','Czechia'),(8,'Ryan Cole','Austin','USA'),(9,'Tom Becker','Berlin','Germany');

INSERT INTO products VALUES
(1,'Laptop Pro','Electronics',1200,15),(2,'Wireless Mouse','Electronics',25,120),
(3,'Desk Chair','Furniture',180,30),(4,'Standing Desk','Furniture',420,12),
(5,'Notebook Set','Stationery',12,300),(6,'Gel Pens','Stationery',8,500),
(7,'Monitor 27in','Electronics',310,22),(8,'Desk Lamp','Furniture',45,60);

INSERT INTO orders VALUES
(1,1,1,1,'2024-01-05','delivered'),(2,2,2,2,'2024-01-09','delivered'),(3,3,3,1,'2024-01-15','delivered'),
(4,1,5,5,'2024-02-01','delivered'),(5,4,4,1,'2024-02-11','shipped'),(6,5,7,2,'2024-02-20','delivered'),
(7,6,2,1,'2024-03-03','cancelled'),(8,7,6,10,'2024-03-10','delivered'),(9,8,1,1,'2024-03-18','shipped'),
(10,2,8,2,'2024-04-02','delivered'),(11,3,7,1,'2024-04-12','pending'),(12,1,3,2,'2024-04-25','delivered'),
(13,4,2,3,'2024-05-06','delivered'),(14,5,1,1,'2024-05-19','delivered'),(15,6,5,4,'2024-06-01','pending'),
(16,7,4,1,'2024-06-14','shipped'),(17,8,6,6,'2024-06-30','delivered'),(18,1,8,1,'2024-07-08','cancelled'),
(19,3,2,2,'2024-07-21','delivered'),(20,2,1,1,'2024-08-05','delivered');
`;

window.BADGES = [
  { id: 'first', icon: '🚀', name: 'First Query', desc: 'Complete your first lesson.', test: s => s.count >= 1 },
  { id: 'five', icon: '📚', name: 'Getting Warm', desc: 'Complete 5 lessons.', test: s => s.count >= 5 },
  { id: 'xp100', icon: '⚡', name: 'Century', desc: 'Earn 100 XP.', test: s => s.xp >= 100 },
  { id: 'join', icon: '🔗', name: 'Join Master', desc: 'Complete the INNER JOIN lesson.', test: s => s.done[10] },
  { id: 'streak3', icon: '🔥', name: 'On Fire', desc: 'Reach a 3-day streak.', test: s => s.streak >= 3 },
  { id: 'window', icon: '🪟', name: 'Window Shopper', desc: 'Complete the Window functions lesson.', test: s => s.done[15] },
  { id: 'all', icon: '🏆', name: 'Course Graduate', desc: 'Complete every lesson of a course.', test: s => s.count >= 17 }
];
