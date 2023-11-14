
import pyodbc
import uuid

conn = pyodbc.connect ('driver={SQL Server};Server=cypress.csil.sfu.ca;user=s_mja90; password=RMLNNge2y4MLAT3m;Trusted_Connection=yes;')

cur = conn.cursor()

global curr_user

print("Connection To Yelp Database Successfully Established")

def verification(userid):
    query="SELECT user_id, name FROM user_yelp WHERE user_id=?"
    cur.execute(query, (userid,))
    user = cur.fetchone()
    if user:
        return user
    return False

#login
def login():
    max_attempts = 3
    print("You have total of 3 attempts to login")
    user_id = input("Please provide me your Yelp user id: ")
    while max_attempts > 0:
        user = verification(user_id)
        max_attempts-=1
        if user:
            print(f"Hi {user[1]}, welcome to Yelp!")
            global curr_user
            curr_user = user[0]
            print(f"System: Current global userid is {user[0]}")
            return user[0]
        print(f"Invalid user id. You have {max_attempts} attempts left. ")
        user_id = input("Please provide me your user id: ")

    print("Attempts used up. Goodbye.")
    return



#Helper function for input value
def get_input_value(prompt, skip_message, field_name):
    value_valid = False

    while not value_valid:
        value = input(prompt)
        print(skip_message)
        if not value:
            value_query = f"SELECT {field_name}(stars) FROM business"
            cur.execute(value_query)
            value = cur.fetchone()[0]
            value_valid = True
        else:
            try:
                value = float(value)
                value_valid = True
            except ValueError:
                print(f"Error: Value should be a number. Please try again.")
                continue

    return value

#Search Business
def search_business():
    
    min_star = get_input_value(
        'Enter the minimum number of stars or press Enter to skip: ',
        '*Note: If skipped, the minimum stars will be set to 0.*',
        "MIN"
    )

    max_star = get_input_value(
        'Enter the maximum number of stars or press Enter to skip: ',
        '*Note: If skipped, the maximum stars will be set to 5.*',
        "MAX"
    )

    city = input('Enter the city name or press Enter to skip: ')
    city = f"%{city}%" if city else "%"

    name = input('Enter the business name or press Enter to skip: ')
    name = f"%{name}%" if name else "%"

    query = "SELECT business_id, name, address, city, stars FROM business WHERE city LIKE ? AND name LIKE ? AND stars <=? AND stars >=? ORDER BY name;"
    cur.execute(query, (city, name, max_star, min_star))

    all_businesses = cur.fetchall()

    if not all_businesses:
        print("No businesses found.")
        return "----------Done----------"

    for row in all_businesses:
        print(f"Business ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Address: {row[2]}")
        print(f"City: {row[3]}")
        print(f"Stars: {row[4]}\n")

    return "---------Done----------"

def get_attribute(attribute_name):
    while True:
        attr_value = input(f"Is the user {attribute_name}? (Yes/No). Note: Yes for {attribute_name} value greater than zero, No for not: ").strip().lower()
        
        if attr_value in ['yes', 'no']:
            return f"{attribute_name} {'> 0' if attr_value == 'yes' else '= 0'}"
        else:
            print("Invalid input. Please enter 'Yes' or 'No'.")

#Search user
def search_user():
    name = input('Enter a keyword for the user name:').strip().lower()
    query = f"""SELECT user_id, name, useful, funny, cool, yelping_since FROM user_yelp
                WHERE name LIKE ? AND {get_attribute('useful')}
                AND {get_attribute('funny')} AND {get_attribute('cool')} ORDER BY name;"""

    cur.execute(query, (f"%{name}%",))
    all_users = cur.fetchall()

    if not all_users:
        print("No users found.")
    else:
        for row in all_users:
            print(f"User ID: {row[0]}\nName: {row[1]}\nUseful: {row[2]}\nFunny: {row[3]}\nCool: {row[4]}\nYelping_Since: {row[5]}\n{'-' * 80}")

#Make friend
def make_friend():
    print("Here are the users you searched for earlier!")
    search_user()

    while True:
        friend_id = input('Which user would you like to befriend? Please enter their user ID: ').strip()

        if not friend_id:
            print('Empty input. Please enter a valid user ID.')
            continue

        cur.execute("SELECT user_id FROM user_yelp WHERE user_id=?", (friend_id,))

        if not cur.fetchone():
            print('User not found. Please enter a valid user ID.')
            continue

        try:
            cur.execute("INSERT INTO friendship VALUES (?, (SELECT user_id FROM user_yelp WHERE user_id=?))", (curr_user, friend_id))
            
            print(f'You are now friends with {friend_id}!')
            break
        except Exception:
            print('You cannot befriend someone you are already friends with.')

# Write Review and helper function
def get_valid_business_id():
    while True:
        business_id = input('Enter the business_id you want to review: ')
        query = "SELECT COUNT(*) FROM business WHERE business_id = ?"
        cur.execute(query, (business_id,))
        count = cur.fetchone()[0]

        if count > 0:
            return business_id
        else:
            print('Invalid business_id. Please try again.')

def get_star_rating():
    while True:
        stars = input('Enter a star rating, range from 1 to 5: ')
        try:
            stars = int(stars)
            if 1 <= stars <= 5:
                return stars
            else:
                print('Star rating must be an integer between 1 and 5. Please try again.')
        except ValueError:
            print('Invalid input. Please enter an integer between 1 and 5.')

def generate_unique_review_id():
    while True:
        temp = str(uuid.uuid4())[:22]
        query = "SELECT review_id FROM review WHERE review_id=?"
        cur.execute(query, (temp,))
        old_review_id = cur.fetchone()

        if not old_review_id:
            return temp

def write_review():
    business_id = get_valid_business_id()
    stars = get_star_rating()
    review_id = generate_unique_review_id()

    query = "insert into review (review_id, business_id, user_id, stars) values ('{0}', '{1}', '{2}', {3})".format(review_id,business_id,curr_user,stars)
    conn.commit()
    return 'Review inserted successfully!'


    
def main():
    if not login():
        print('You are not a valid user, please give a valid username')
        return

    running = True
    while running:
        print('\n')
        print("Thank you for using Yelp! :") 
        print('Please select one of the following function')
        print('0. Exit')
        print('1. Search busniess')
        print('2. Search user')
        print('3. Make Friend')
        print('4. Write a Reivew')
        user_input = input('Please select from 0 to 4: ')
        print('You select function: '+user_input)
        if int(user_input)==0:
            print('Exited. Goodbye.')
            running=False
            
        elif int(user_input) == 1:
            print('Going to search busniess function')
            print (search_business())
            
        elif int(user_input) ==2:
            print('Going to search users function')
            print(search_user())
        elif int(user_input)==3:
            print('Going to make friend function')
            print(make_friend())
        elif int(user_input) == 4:
            print('Going to write review function')
            print(write_review())
        else:
            print('Invalid input, please select from 0-4.')

main()
conn.close()
print("Connection closed")
