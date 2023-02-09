import phonenumbers as pn
  
# importing geocoder from phonenumbers
from phonenumbers import geocoder
  
# input phone number with country code
phoneNumber = "+917395971053"
phoneNumber = pn.parse(phoneNumber)
  
# printing the required country for that phone number
print(phoneNumber.national_number)