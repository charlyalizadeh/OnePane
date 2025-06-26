# AXERIA Device Data Integrity Report

Project to check if the following directory/software have the same users/devices:

[ ] ActiveDirectory
[ ] ManageEngine ActiveDirectory
[x] ManageEngine Endpoint
[ ] OneDrive (SharePoint, OneDrive, Exchange)
[x] Intune
[x] Microsoft Entra
[x] Tenable

Ideally this program would extract the data automatically through their API.
This would requires giving this application rights to read a lot of AXERIA internal data.
So for the moment the data is extracted manually and imported in this program using export files.

## Automated import

### Selenium and Chrome Webdriver

To collect the data from Intune and Entra ID the driver go to the respective website and automatically download the data
(using their respective export to csv features). However to do so you need to be connected to Microsoft, even though we could
connect to Microsoft everytime we run this code, it is not optimal and in the case you want to run it multiple times in a short period
of time Microsoft will lock the SMS code verification.
To fix that problem we create a Chrome profile by copying the default one into this project directory.
**IT IS VERY IMPORTANT THAT THE PROFILE DIRECTORY IS NOT IN THE DEFAULT CHROME DATA PATH**.
Indeed for security reasons Chrome has deactivated automated controll for profile located in the default chrome data path.
After creating a new profile we need to connect to Microsoft a first time. To do so you need to enter your email, password and the 
code you'll recieve by SMS. This operation should only be done the first time you run this project on your computer.


## Implementation motivation

The implementation is not using OOP as a conscient choice.
Even though using OOP may help with maintainenace, I think it would decrease the readability.
Please, don't refactor this code using OOP except if you know what you are doing and have good motivation to do so.
