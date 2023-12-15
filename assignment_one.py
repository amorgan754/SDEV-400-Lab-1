"""This program is to demonstrate the capabilities to modify in S3 buckets"""

#imports
import sys
from datetime import datetime
import logging
import random
import boto3
from botocore.exceptions import ClientError
import botocore



date = datetime.now()
currentDate = date.strftime("%m/%d/%Y %H:%M")

#s3 client
s3 = boto3.client("s3")

#region
REGION = "us-east-1"

#function to validate name entry
def name_check(name):
    """This function is to validate name characters"""
    name_input = input("Enter " + name + " name: ")
    while not name_input.isalpha():
        print("Incorrect format.")
        name_input = input("Enter " + name + " name: ")
    return name_input

#Function of the menu
def main_menu():
    """This function is to define the main menu"""
    print("Option 1: Create a S3 bucket")
    print("Option 2: Put objects into a created bucket")
    print("Option 3: Delete an object in a bucket")
    print("Option 4: Delete a bucket")
    print("Option 5: Copy one object from one bucket to another")
    print("Option 6: Download an existing object from a bucket")
    print("Option 0: Exit the program")

#function to see if the bucket name exists
def already_bucket(bucket_name):
    """This function is to validate if there is already an existing bucket"""
    try:
        response = s3.head_bucket(Bucket = bucket_name)
    except ClientError as error:
        logging.debug(error)
        return False
    return response

#function to display all of the buckets
def display_buckets():
    """This function is to display all current buckets"""
    bucket_list = s3.list_buckets()
    buckets = [bucket["Name"] for bucket in bucket_list ["Buckets"]]

    print("Current buckets")
    print(buckets)

#function to see if bucket is empty
def bucket_check(bucket_name):
    """This function is to see if a bucket is empty before it is deleted"""
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
    except ClientError as error:
        logging.error(error)
        return False
    return response
#function to list bucket files
def list_objects(bucket_name):
    """This function is to list the files in a bucket"""
    for key in s3.list_objects(Bucket=bucket_name)['Contents']:
        print(key['Key'])


def delete_all(bucket_name):
    """This function is to delete all in a bucket"""

    response = s3.list_objects_v2(Bucket=bucket_name)
    files = response['Contents']
    files_to_delete = []
    for file in files:
        files_to_delete.append({"Key": file["Key"]})
    response = s3.delete_objects(
        Bucket=bucket_name, Delete={"Objects": files_to_delete})
    return response


def bucket_name_check():
    """This function is to validate two function names are not the same"""
    display_buckets()
    print(" ")

    bucket_name_one = input("What is the first bucket?: ")
    bucket_name_two = input("What is the second  bucket?: ")

    while bucket_name_one == bucket_name_two:
        print("  ")
        print("The buckets can not be the same.")
        print("Please reinput")
        print(" ")

        bucket_name_one = input("What is the first bucket?: ")
        bucket_name_two = input("What is the second  bucket?: ")

    return bucket_name_one, bucket_name_two

#The following functions will be functions for the use of the menu

#Function to create s3 buckets
    #FirstnameLastnameDigits
def create_bucket():
    """This function is to create a bucket"""
    random_number = str(random.randrange(000000, 999999, 6))

    #input and validate first name
    print("\nWe will create a bucket with your first and last name")
    print(" ")

    first_name = name_check("first")

    #input and validate last name
    last_name = name_check("last")


    bucket_name = first_name + last_name + random_number

    #check to see if there is already a bucket with that name
    while already_bucket(bucket_name):
        bucket_name = first_name + last_name + "-" + random_number
    try:
        s3_client =  boto3.client("s3", region_name = REGION)
        #location = {"LocationConstraint": region}
        s3_client.create_bucket(Bucket = bucket_name) #CreateBucketConfiguration = location)
        print(" ")
        print("Successful creation of bucket: " + bucket_name)
        print(" ")
    except ClientError as error:
        logging.error(error)
        return False
    return True




#Funcion to put objects in created bucket
def object_in_bucket():
    """This function is to put error log in a created bucket"""
    #display all buckets available
    display_buckets()
    #bucket name
    bucket_name = input("What is the name of the bucket you are putting it into?: ")
    #file location
    file = "Support/error.log"

    #moving file to the bucket
    try:
        s3.put_object(Bucket = bucket_name, Key = file)
        print(" ")
        print("error.log was sucessfully put into bucket " + bucket_name)
        print(" ")
    except ClientError as error:
        logging.error(error)
        return False
    return True

#Function to delete object in bucket
def delete_object():
    """This function is to delete an object in a bucket"""
    #list all available buckets
    print(" ")
    display_buckets()

    #select bucket
    print(" ")
    bucket_name = input("Please select which bucket you would like to delete from: ")
    print(bucket_name)

    print(" ")
    for key in s3.list_objects(Bucket=bucket_name)['Contents']:
        print(key['Key'])
    print(" ")
    file_name = input("Please select the file you would like to delete: ")

    #select file for deletion
    try:
        s3.delete_object(Bucket = bucket_name, Key = file_name)
        print(" ")
        print("error.log was sucessfully deleted from bucket " + bucket_name)
        print(" ")
    except ClientError as error:
        logging.error(error)
        return False
    return True


#Function to delete a bucket
def delete_bucket():
    """This function is to delete a bucket"""
    #all available buckets
    print(" ")
    display_buckets()

    #select bucket
    print(" ")
    bucket_name = input("Please select which bucket you would like to delete: ")

    #see if bucket is empty
    print(" ")
    validation = bucket_check(bucket_name)

    #delete bucket
    if validation is False:
        print("Bucket is not empty. Do you want to delete it?")
        delete_bucket_object = input("Yes or No?: ")
        if delete_bucket_object.lower() == "yes":
            try:
                delete_all(bucket_name)
                s3.delete_bucket(Bucket = bucket_name)
                print(" ")
                print(bucket_name + " was sucessfully deleted")
                print(" ")
            except ClientError as error:
                logging.error(error)
                return False
        else:
            print(" ")
            print("You have decided to not delete the bucket")
            print(" ")
    else:
        try:
            s3.delete_bucket(Bucket = bucket_name)
            print(" ")
            print(bucket_name + " was sucessfully deleted")
            print(" ")
        except ClientError as error:
            logging.error(error)
            return False
        return True

#function to copy one object from one bucket to another
def copy_object():
    """This function is to copy an object from one bucket to another"""

    #list all available buckets
    print(" ")

    #select bucket to copy from
    print(" ")
    bucket_name_one, bucket_name_two = bucket_name_check()
    print(" ")

    print(" ")
    print("Current files in ", bucket_name_one, " are: ")

    for key in s3.list_objects(Bucket=bucket_name_one)['Contents']:
        print(key['Key'])
    print(" ")

    file = input("Please select the file you would like to copy: ")

    #copy and move error log
    source = {'Bucket': bucket_name_one, 'Key': file}
    try:
        s3.copy_object(CopySource = source, Bucket = bucket_name_two,
            Key = file)
        print(" ")
        print(file, " sucessfully copied")
        print(" ")
    except ClientError as error:
        logging.error(error)
        return False
    return True


#Function to download existing object from bucket
def download_object():
    """This function is to download an existing object from a bucket"""
    #list all available buckets
    print(" ")
    display_buckets()

    #select which bucket to download from
    print(" ")
    bucket_name = input("Please select which bucket you would like to download from: ")

    for key in s3.list_objects(Bucket=bucket_name)['Contents']:
        print(key['Key'])

    file = input("What file would you like to download?: ")

    file_name = input("What would you like to call the file?: ")

    #donwload file
    try:
        s3.download_file(bucket_name, file, file_name)
        print(" ")
        print("File downloaded")
        print(" ")
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "404":
            print("The error log from this bucket does not exist")
        else:
            raise


#Function to exit the program
    #Will display the date and time
def exit_program():
    """This function is to exit the program"""
    print("\nThank you for using our program.")
    print("It is currently ", currentDate)
    sys.exit(0)



#running of the program

#logging
#logging.basicConfig(level = logging.DEBUG, format = '%(levelname)s: %(asctime)s: %(message)s')


#use while loop
CHOICE = None

#keeps running the while loop until selected to exit the program
while CHOICE != 0:
    main_menu()

    CHOICE = input("Please select a menu choice: \n")

    if CHOICE == "1":
        if create_bucket():
            logging.info("created bucket")
        else:
            print("Error")
    elif CHOICE == "2":
        object_in_bucket()
    elif CHOICE == "3":
        delete_object()
    elif CHOICE == "4":
        delete_bucket()
    elif CHOICE == "5":
        copy_object()
    elif CHOICE == "6":
        download_object()
    elif CHOICE == "0":
        exit_program()
    else:
        print("\nPlease make a valid choice\n")
