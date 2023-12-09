# YOUR PROJECT TITLE
#### Video Demo:  <URL https://youtu.be/GOrnOLAkFTc>
#### Description:
This is a web  application for managing your finances, and it's built using Python, HTML, CSS, SQL, and Flask. It's organized in a "project" folder with several subfolders:
### static:
This folder contains the webpage's logo in a .png file and the style.css file for various page elements. The main page's design primarily uses the Bootstrap library to ensure it's flexible for different screen sizes.
### templates:
In this folder, you'll find all the HTML pages that the web application displays. The main page is called **layout.html** and other pages are based on this template using Django and Jinja. It includes a navigation bar at the top, allowing users to access different parts of the app, and this navigation bar dynamically adjusts based on whether the user is logged in. Additionally, at the bottom of the page, there's a quote.
- The **login.html** and **register.html** are similar in terms of their front-end design. They both have forms for users to enter their username and password.
- **index.html** is the main page. It features a header that varies depending on whether there's an error or if it can show the last update. The main body includes a form where users can input details like the date, description, amount, account, and purpose of a transaction. Below this form, there's a summary table displaying current cash, money spent, and money earned. Towards the bottom, the page lists the last 10 transactions.
- **history.html** and **history_change.html** display tables with all the transactions stored in the SQL database. Users can edit or delete transactions from here.
- **add_Account.html** provides a simple form for adding an account or purpose, along with two tables listing all the accounts and purposes created.
- **account_filter.html** shows information about a single account based on a query. It also displays a summary of the filtered data and allows users to apply date or period filters.
### mybudget.db
This data base contains four tables.
- **users:** Stores user data, including user IDs, usernames, hashed passwords, and available cash.
- **transactions:** Contains information about financial transactions, including transaction IDs, user IDs, dates, amounts, descriptions, purposes, and shared spaces for event expenses.
- **accounts:** Manages accounts and includes IDs, user IDs, account names, and optional description text.
- **subaccounts:**  Contains subaccount details with IDs, user IDs, name-purposes, and associated account numbers.
### helpers.py
This file includes two functions: **cop** displays money in HTML in a specific format, such as "$123,135". **login_required** checks if a user has already log in, if not, it redirects them to the login page
### app.py
This Python file contains a range of functions:
- **login():** This function handles both GET and POST requests. In the GET request, it displays the login page, and in the POST request, it verifies the username and password. If the credentials are correct, a session for the user is created, and they are redirected to the index page.
- **logout():** This function clears the session and redirects the user to the login page.
- **register():** Similar to login, this function handles both GET and POST requests. The GET request displays the registration page, while the POST request validates user information. If the data is correct, it creates the user and updates the users table.
- **index():** This function only handles GET requests. It retrieves user information from the users, transactions, accounts, and subaccounts tables to display on the page.
- **addtransfer():** This function only handles the POST request. It validates transaction information, updates the user's cash balance, and adds the transaction to the table.
- **history():** This function handles both GET and POST requests. The GET request looks for the transactions history in SQL table and display it on the page. The POST request looks the button pressed with the "action" request form. "0" means the user delete a transaction,and the program update the transaction table and the cash available in the user table. "1" means the user want to edit a single transaction, the program validates the data and update the tables. "2" means the user want to edit a different transaction and history_change.html will be displayed.
- **add_account():** Similar to other functions, this one handles both GET and POST requests. It adds an account based on the button pressed and updates the account and subaccount tables.
- **filter():** : Lastly, this function handles both GET and POST requests. The GET request filters transaction history for a single account. The POST request allows users to filter transactions by start and end dates.
