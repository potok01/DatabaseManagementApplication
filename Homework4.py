#!/usr/bin/python3

#Author: Adrian Potok
#Class: CS4430
#Date 4/4/2022

import mysql.connector as dbconn
from mysql.connector import errorcode
from datetime import datetime

def main():
	#Connection configuration
	config = {
  		'user': 'cs4430',
  		'password': 'cs4430',
  		'host': 'localhost',
  		'database': 'northwind',
  		'raise_on_warnings': True
	}
	
	#Text for user interface
	option_not_found_text = "This is not a valid option, please type help for a list of options, or enter an option."
	options_text = "\nPlease select one of the following options by typing the associated number and pressing enter.\n1. Add a customer\n2. Add an order\n3. Remove an order\n4. Ship an order \n5. Print pending orders with customer information\n6. More options\n7. Exit\n"
	username_password_error_text = f"This program is setup to use the username={config['user']} and the password={config['password']}, however the mysql environment on this system does not appear to contain a USER entry with those credentials."
	database_not_found_error_text = f"The program is setup to use database={config['database']}, however the msql environment on this system does not appear to contain a DATABASE entry with that name."
	add_customer_text = "\nAdd customer has been selected, please fill in the information below"
	add_order_text = "\nAdd order has been selected, please fill in the information below"
	remove_order_text = "\nRemove order has been selected"
	ship_order_text = "\nShip order has been selected"
	print_pending_orders_text = "\nPrint pending orders has been selected, printing pending orders in ascending order date... "
	error_text = "There has been an error as described by the above error message, enter c to reenter data or anything else to return to the main menu: "
	
	
	#Entity Attributes
	customers_attributes = ["Company", "LastName", "FirstName", "Email", "JobTitle", "BusinessPhone", "HomePhone", "MobilePhone", "Fax", "Address", "City", "State", "ZIP", "Country", "Web", "Notes", "Attachments"]
	orders_attributes = ["EmployeeID", "CustomerID", "OrderDate", "ShippedDate", "ShipperID", "ShipName", "ShipAddress", "ShipCity", "ShipState", "ShipZIP", "ShipCountry", "ShippingFee", "Taxes", "PaymentType", "PaidDate", "Notes", "TaxRate", "TaxStatus", "StatusID"]
	order_details_attributes = [ "OrderID","ProductID","Quantity","UnitPrice","Discount","StatusID","DateAllocated","PurchaseOrderID","InventoryID"]
	inventory_transactions_attributes = ["TransactionType", "TransactionCreatedDate", "TransactionModifiedDate", "ProductID", "Quantity", "PurchaseOrderID", "CustomerOrderID", "Comments"]
	
	#Entity Attributes For Nice Printing
	customers_attributes_formatted = ["Company", "Last name", "First name", "Email address", "Job title", "Business phone number", "Home phone number", "Mobile phone number", "Fax number", "Address", "City", "State", "ZIP", "Country", "Website", "Notes", "Attachments"]
	orders_attributes_formatted = ["Employee ID", "Customer ID", "Order date (yyyy-mm-dd hh:mm:ss)", "Shipped date (yyyy-mm-dd hh:mm:ss)", "Shipper ID", "Ship name", "Ship address", "Ship to city", "Ship to state", "Ship to ZIP", "Ship to country", "Shipping fee", "Taxes", "Payment type", "Paid date (yyyy-mm-dd hh:mm:ss)", "Notes", "Tax rate", "Tax status", "Order status ID"]
	order_details_attributes_formatted = ["Order ID", "Product ID", "Quantity", "Unit price", "Discount", "Order details status ID", "Date allocated (yyyy-mm-dd hh:mm:ss)", "Purchase order ID", "Inventory ID"]
	inventory_transactions_attributes_formatted = ["Transaction type", "Transaction created date (yyyy-mm-dd hh:mm:ss)", "Transaction modified date (yyyy-mm-dd hh:mm:ss)", "Product ID", "Quantity", "Purchase order ID", "Customer order ID", "Comments"]
	
	#SQL Dictionary Tried to put most statements here
	sql = {
		'Transaction type' : 'SELECT ID FROM Inventory_Transaction_Types',
		'Customer order ID' : 'SELECT OrderID FROM Orders',
		'Order ID' : "SELECT OrderID FROM Orders",
		'Employee ID' : "SELECT ID FROM Employees",
		'Customer ID' : "SELECT ID FROM Customers",
		'Shipper ID' : "SELECT ID FROM Shippers",
		'Tax status' : "SELECT ID FROM Orders_Tax_Status",
		'Product ID' : "SELECT ID FROM Products",
 		'Order status ID' : "SELECT StatusID FROM Orders_Status",
		'Order details status ID' : "SELECT StatusID FROM Order_Details_Status",
		'add_customer' : "INSERT INTO Customers (" + ",".join(customers_attributes) + ") VALUES (" + ",".join(["%s"] * len(customers_attributes)) + ")",
		'add_order' : "INSERT INTO Orders (" + ",".join(orders_attributes) + ") VALUES (" + ",".join(["%s"] * len(orders_attributes)) + ")",
		'add_order_details' : "INSERT INTO Order_Details (" + ",".join(order_details_attributes) + ") VALUES (" + ",".join(["%s"] * len(order_details_attributes)) + ")",
		'add_transaction' : "INSERT INTO Inventory_Transactions (" + ",".join(inventory_transactions_attributes) + ") VALUES (" + ",".join(["%s"] * len(inventory_transactions_attributes)) + ")"
	}
	
	#Connect to database
	try:
		db = dbconn.connect(**config)
	except dbconn.Error as err:
	
		#Wrong username and password
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print(username_password_error_text)
			quit()
		
		#Wrong database name
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print(database_not_found_error_text)
			quit()

		#Catch all other erros
		else:
			print("Unknown error with database, it is possible mysql is not installed")
			quit()

	
	#Begin application loop
	while True:
		#menu is a boolean to control if the user should exit an option to the main menu
		menu = False
		user_input = input(options_text)
		
		#Add a customer
		if user_input == "1":
			print(add_customer_text)
			while not menu:
				customer_data = []
				
				#loop through customers attributes and have the user fill them in
				for attribute in customers_attributes_formatted:
					customer_data.append(input(f"{attribute}: " ))
					
				#Convert_to_none takes a list and
				customer_data = convert_to_none(customer_data)
				cursor = db.cursor()
				
				#Try to execute all sql statements in try except suites to catch errors from the sql
				try:
					cursor.execute(sql['add_customer'],customer_data)
					cursor.close()
					confirmation_prompt(db)
					break
				except dbconn.Error as err:
					print(err.msg)
					
					#Ask the user if they want to try again if there was an unknown error
					user_input = input(error_text)
					if user_input.lower() == "c":
						continue
					else:
						break
		#Add an order				
		elif user_input == "2":
			print(add_order_text)
			while not menu:
			
				#The orders attributes are added using a function called checker, and a different argument is passed depending on the attribute. For instance, a string need no input validation, so the input is directly added to the list, but a float or date must be validated. Finally, the foreign key constrains must be checked, and it also happens that the foreign keys are all ints so the type is also checked
				order_data = []
				for attribute in orders_attributes_formatted:
					
					#Lists to identify what each attribute needs to be checked for
					foreign_keys = ["Employee ID", "Customer ID", "Shipper ID", "Tax status", "Order status ID"]
					floats = ["Shipping fee", "Tax rate", "Taxes"]
					dates = ["Order date (yyyy-mm-dd hh:mm:ss)", "Shipped date (yyyy-mm-dd hh:mm:ss)", "Paid date (yyyy-mm-dd hh:mm:ss)"]
					
					#A different function is passed to checker() depending on which catagory it is in as listed above, for instance to type check the date, I pass the date_func()
					if menu:
						break
					elif attribute in dates:
						order_data, menu = checker(order_data, attribute, date_func, db)
					elif attribute in foreign_keys:
						order_data, menu = checker(order_data, attribute, foreign_key_func, db, sql[attribute])
					elif attribute in floats:
						order_data, menu = checker(order_data, attribute, float_func, db)
					else:
						order_data.append(input(f"{attribute}: "))
				
				order_data = convert_to_none(order_data)
				if menu:
					break
					
				#Loop to determine number of products attached to an order
				while True:
					try:
						number_of_products = int(input("Please enter the number of products attached to this order as an integer: "))
						break
					except:
						print("The number of products was not entered correctly.")
				
				#Same thing done for Orders now for Order_Details
				order_details_data = []
				for i in range(0,number_of_products):
					product = []
					print("")
					print(f"Product {i+1}")
					for attribute in order_details_attributes_formatted[1:]:
						foreign_keys = ["Product ID", "Order details status ID"]
						ints = ["Purchase order ID", "Inventory ID"]
						floats = ["Quantity", "Unit price", "Discount"]
						dates = ["Date allocated (yyyy-mm-dd hh:mm:ss)"]
						if menu:
							break
						elif attribute in ints:
							product, menu = checker(product, attribute, int_func, db)
						elif attribute in dates:
							product, menu = checker(product, attribute, date_func, db)
						elif attribute in foreign_keys:
							product, menu = checker(product, attribute, foreign_key_func, db, sql[attribute])
						elif attribute in floats:
							product, menu = checker(product, attribute, float_func, db)
						else:
							product.append(input(f"{attribute}: "))
					order_details_data.append(convert_to_none(product))
					
					if menu:
						break
				
				if menu:
					break

				#All sql is again in the try statement
				try:
					cursor = db.cursor(buffered=True)
					cursor.execute(sql['add_order'],order_data)
					
					#Get the order_id of the order just inserted
					order_id = cursor.lastrowid
					
					#Add each order detail
					for i in range(0,len(order_details_data)):
						order_details_data[i] = [order_id] + order_details_data[i]
						cursor.execute(sql['add_order_details'],order_details_data[i])
					
					cursor.close()
					confirmation_prompt(db)
					break
				except dbconn.Error as err:
					db.rollback()
					print(err.msg)
					user_input = input(error_text)
					if user_input.lower() == "c":
						continue
					else:
						menu = True
						break
			
			
		#Remove an order
		elif user_input == "3":
			print(remove_order_text)
			while not menu:
				while True:
					try:
						order_id = int(input("Please enter the id of the order to be deleted as an integer: "))
						cursor = db.cursor(buffered=True)
						cursor.execute(sql['Order ID'])
						
						#Retreive all order ids
						ids = []
						for tup in cursor:
							for element in tup:
								ids.append(element)
				
						#Check if user entered orderid exists
						if order_id not in ids:
							raise IDNotFoundError
						
						#There are foreign key constrains linked to order_id and thus we must delete any link to the order_id in other tables before delteting the order from Orders
						query = f"DELETE FROM Inventory_Transactions WHERE CustomerOrderID={order_id}"
						cursor.execute(query)	
						query = f"DELETE FROM Invoices WHERE OrderID={order_id}"
						cursor.execute(query)	
						query = f"DELETE FROM Order_Details WHERE OrderID={order_id}"
						cursor.execute(query)
						query = f"DELETE FROM Orders WHERE OrderID={order_id}"
						cursor.execute(query)
						
						cursor.close()
						confirmation_prompt(db)
						menu = True
						break
						
					except ValueError:
						user_input = input("The order id was not properly entered. Press c to reenter the order id or anything else to return to the main menu.")
						if user_input == "c":
							continue
						else:
							menu = True
							break
							
					except IDNotFoundError:
						user_input = input("The order id entered could not be found in the list of order ids. Press c to reenter the order id or anything else to return to the main menu.")
						if user_input == "c":
							continue
						else:
							menu = True
							break
			
		#Ship order
		elif user_input == "4":
			print(ship_order_text)
			while not menu:
				while True:
					try:
						order_id = int(input("Please enter the id of the order to be shipped as an integer: "))
						cursor = db.cursor(buffered=True)
						cursor.execute(sql['Order ID'])
						
						#Get all orderids
						ids = []
						for tup in cursor:
							for element in tup:
								ids.append(element)
				
						#Make sure order id exists
						if order_id not in ids:
							raise IDNotFoundError
							
						#Get all products and their quantites from the associated order
						query = f"SELECT ProductID,Quantity FROM Order_Details WHERE OrderID = {order_id}"
						cursor.execute(query)
						
						products = []
						for tup in cursor:
							product = []
							for element in tup:
								product.append(element)
							products.append(product)
							
						
						
						for product_id, quantity in products:
							
							#Get all purchased stock for a certain product
							query = f"SELECT sum(Quantity) FROM Inventory_Transactions WHERE ProductID={product_id} AND TransactionType=1"
							cursor.execute(query)
							
							purchased = []
							for tup in cursor:
								for element in tup:
									purchased.append(element)
							
							#Get all sold or held stock of a certain product
							query = f"SELECT sum(Quantity) FROM Inventory_Transactions WHERE ProductID={product_id} AND (TransactionType=2 OR TransactionType=3)"
							cursor.execute(query)
							
							sold_or_held = []
							for tup in cursor:
								for element in tup:
									sold_or_held.append(element)
									
							purchased = float(purchased[0])
							sold_or_held = float(sold_or_held[0])
							
							#Check if total inventory for a certain product is greater than or equal to quantity requested in the order
							if purchased-sold_or_held < float(quantity):
								raise LowStockError(product_id)
							
							#Fill in transaction data
							transaction_data = []
							transaction_data.append(2)
							transaction_data.append(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
							transaction_data.append("")
							transaction_data.append(product_id)
							transaction_data.append(quantity)
							transaction_data.append("")
							transaction_data.append(order_id)
							transaction_data.append(input(f"Comments on the transaction of product ID = {product_id}: "))
							
							order_data = convert_to_none(transaction_data )
							cursor.execute(sql['add_transaction'],transaction_data)
						
						#Fill in shipping data
						print("Please enter the following data about the shipment")
						shipping_data = []
						
						shipping_data, menu = checker(shipping_data, "Shipped date (yyyy-mm-dd hh:mm:ss)", date_func, db)
						shipping_data, menu = checker(shipping_data, "Shipper ID", foreign_key_func, db, sql["Shipper ID"])
						shipping_data, menu = checker(shipping_data, "Shipping fee", float_func, db)
						shipping_data.append(order_id)
						
						shipping_data = convert_to_none(shipping_data)
						query = "UPDATE Orders SET ShippedDate = %s, ShipperId = %s, ShippingFee = %s WHERE OrderID = %s"
						cursor.execute(query,shipping_data)
							
						cursor.close()
						confirmation_prompt(db)
						menu = True
						break
						
					except ValueError:
						user_input = input("The order id was not properly entered. Press c to reenter the order id or anything else to return to the main menu.")
						if user_input == "c":
							continue
						else:
							menu = True
							break
					except TypeError:
						print(f"This order can not be shipped because one or more of the orders have null quantities")
						db.rollback()
						menu = True
						break
							
					except IDNotFoundError:
						user_input = input("The order id entered could not be found in the list of order ids. Press c to reenter the order id or anything else to return to the main menu.")
						if user_input == "c":
							continue
						else:
							menu = True
							break
					except LowStockError as lse:
						product_id = str(lse.get_product_id())
						print(f"This order can not be shipped because there is not enough product ID = {product_id} to ship the order")
						db.rollback()
						menu = True
						break
						
					
		#Print pending order
		elif user_input == "5":
			print(print_pending_orders_text)
			
			#Get all orders whose shipdate is null and order them by order date
			query = "SELECT * FROM Orders WHERE ShippedDate IS NULL ORDER BY OrderDate"
			cursor = db.cursor(buffered=True)
			cursor.execute(query)
			
			#Nicely print the orders
			orders = []
			for item in cursor:
				orders.append(item)
			order_attributes = ["Order ID"] + orders_attributes_formatted
			print("")
			for order in orders:
				for i in range(len(order_attributes)):
					print(order_attributes[i] + f": {order[i]}")
				print("")
			
		elif user_input == "6":
			print("More options, I did not choose to add more options")
		
		elif user_input == "7":
			print("Exiting...")
			db.close()
			exit()
			
		elif user_input.lower() == "help":
			pass
			
		else:
			print(option_not_found_text)

#This is a confirmation prompt that always pops up before committing any changes to the database		
def confirmation_prompt(db):
	rollback_text = "The changes made to the database have been successfully rolled back."
	commit_text = "The changes made to the database have been successfully committed."
	confirmation_text = "\nAre you sure that the changes should be committed to the database? Y for yes, anything else for no: "
	user_input = input(confirmation_text)
	if user_input.lower() == "y":
		db.commit()
		print(commit_text)
	else:
		db.rollback()
		print(rollback_text)

#Takes a list, converts all "" in the list into None, then returns the list. This is done because that is what is required to get a Null value in sql
def convert_to_none(li):
	for i in range(0,len(li)):
		if li[i] == "":
			li[i] = None
		else:
			pass
	return li

#This is the function passed to the checker to perform all the necessary input validation for foreign keys
def foreign_key_func(li, attribute, user_input, db, sql):
	cursor = db.cursor(buffered=True)
	cursor.execute(sql)
	
	#Get a list of the attribute from it associated table
	ids = []
	for tup in cursor:
		for element in tup:
			ids.append(element)
	cursor.close()
	
	#Check to see if the user_input attribute is in the list of all attributes
	user_input = int(user_input)
	
	#If not raise foreign key error to indicate the value entered by the user does not exist and would therefore violate the foreign key constraints of the database
	if user_input not in ids:
		raise ForeignKeyError(attribute)
	else:
		#This is a special section only for product ID because it must be checked to see if the product is discontinued
		if attribute == "Product ID":
			
			#Get the discontinued status of the product
			cursor = db.cursor(buffered=True)
			query = f'SELECT Discontinued FROM Products WHERE ID={user_input}'
			cursor.execute(query)
			for tup in cursor:
				for element in tup:
					discontinued = element
				
			#If discontinued reject product, else add product
			if discontinued == 1:
				print("This order must be rejected on the basis that the product ID entered has been discontinued. Returning to menu...")
				return True
			else:
				li.append(user_input)
				return False
		else:
			li.append(user_input)
			return False

#This is the function for int input validation	
def int_func(li, attribute, user_input, db, sql=None):
	li.append(int(user_input))
	return False

#This is the function for float input validation	
def float_func(li, attribute, user_input, db, sql=None):
	li.append(float(user_input))
	return False
	
def date_func(li, attribute, user_input, db, sql=None):
	li.append(datetime.strptime(user_input,'%Y-%m-%d %H:%M:%S'))
	return False

#This is the checker function that ensures the format of the data matches what is requested by the database	
def checker(li, attribute, func, db, sql=None):
	menu = False
	value_error_text = "The entered format for data does not match what has been requested, enter c to reenter the data or anything else to return to the main menu: "
	
	#Keep looping to give the user a chance to ammend how they have entered the data if they make a mistake
	while True:
		try:
			user_input = input(f"{attribute}: " )
			
			#If user input not intended to be null then do input validation. Here menu catches a boolean value so that the program can immediately return to menu if a discontinued product ID is entered
			if not user_input == "":
				menu = func(li, attribute, user_input, db, sql)
			else:
				li.append("")
			break
			
		except ValueError:
			user_input = input(value_error_text)
			if user_input.lower() == "c":
				continue
			else:
				menu = True
				break
				
		except ForeignKeyError as fke:
			field = fke.get_field()
			user_input = input(f"The {field} field is constrained by a foreign key constraint, please make sure the data entered follows this constraint and the ID entered already exists in its appropriate table. Enter c to reenter the data or anything else to return to the main menu: ")
			if user_input.lower() == "c":
				continue
			else:
				menu = True
				break
		
	return li, menu
	

#These custom exceptions are just to improve the readability of the code, some of them can also contain information to provide more informative error messages
class ForeignKeyError(Exception):
	def __init__(self,field):
		self.__field = field
	
	def get_field(self):
		return self.__field
		
class IDNotFoundError(Exception):
	pass
	
class LowStockError(Exception):
	def __init__(self,product_id):
		self.__product_id = product_id
	
	def get_product_id(self):
		return self.__product_id
	
main()
		

	

