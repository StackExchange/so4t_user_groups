# Stack Internal User Groups (so4t_user_groups)
An API script for Stack Internal that adds users to user groups based on the contents of a CSV file.

## Requirements
* An instance of Stack Internal (Enterprise) (no support for Business tier yet)
* Python 3.7 or higher ([download](https://www.python.org/downloads/))
* Operating system: Linux, MacOS, or Windows

## Setup

[Download](https://github.com/StackExchange/so4t_user_groups/archive/refs/heads/main.zip) and unpack the contents of this repository

**Installing Dependencies**

* Open a terminal window (or, for Windows, a command prompt)
* Navigate to the directory where you unpacked the files
* Install the dependencies: `pip3 install -r requirements.txt`


**API Authentication**

For the Business tier, you'll need a [personal access token](https://stackoverflowteams.help/en/articles/4385859-stack-overflow-for-teams-api) (PAT). You'll need to obtain an API key and an access token for Enterprise. Documentation for creating an Enterprise key and token can be found within your instance at this url: `https://[your_site]/api/docs/authentication`

**Generating an Access Token (Enterprise)**

For secure Access Token generation, follow the [Secure API Token Generation with OAuth and PKCE](https://support.stackenterprise.co/support/solutions/articles/22000294542-secure-api-token-generation-with-oauth-and-pkce) guide.

**Note on Access Token Requirements:**
While API v3 now generally allows querying with just an API key for most GET requests, certain paths and data (e.g., `/images` and the email attribute on a `User` object) still specifically require an Access Token for access. If you encounter permissions errors on such paths, ensure you are using an Access Token.


**Populate the CSV template**

In the [Templates folder](https://github.com/StackExchange/so4t_user_groups/tree/main/Templates), you'll find a CSV file called `users.csv`. This is the file you'll use to indicate which users you want to be added to which user groups. 

There are two columns in the CSV:
* `user_email_or_id` - the unique identifier for the user that you want to assign to a user group. You can use either the user's email address or Stack Internal user ID. If neither the email address nor the user ID exist in your Stack Internal database, the script will skip that row and notify you via the terminal window.
* `group_name_or_id` - the unique identifier for the user group that you want to assign to the user. You can use either a group name or group ID. If you use a name that doesn't exist, the script will create a new user group with that name.

Only a single user and group can be added per line. If you'd like to add multiple users to a single group, you'll need to create a separate line for each user. Likewise, if you'd like to add a single user to multiple groups, you'll need to create a separate line for each group.

## Usage

In a terminal window, navigate to the directory where you unpacked the script. 
Run the script using the following format, replacing the URL, token, and/or key with your own:

`python3 so4t_user_groups.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --csv "PATH_TO_CSV"`

**Example for Stack Internal (Enterprise):**
`python3 so4t_user_groups.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --csv "users.csv"`

The script can take a minute or two to run, particularly as it gathers data via the API. As it runs, it will update the terminal window with the tasks it performs. The script will return you to a command line prompt when it is complete.

## Support, security, and legal
If you encounter problems using the script, please leave feedback in the Github Issues. You can also clone and change the script to suit your needs. It is provided as-is, with no warranty or guarantee of any kind.

All data is handled locally on the device from which the script is run. The script does not transmit data to other parties, such as Stack Overflow. All of the API calls performed are read only, so there is no risk of editing or adding content on your Stack Internal instance.
