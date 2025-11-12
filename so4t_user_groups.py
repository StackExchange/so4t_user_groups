'''
This Python script is a working proof of concept example of using Stack Internal APIs for adding user to user groups. 
If you run into difficulties, please leave feedback in the Github Issues.
'''

# Standard library imports
import argparse
import csv

# Local libraries
from so4t_api_v2 import V2Client
from so4t_api_v3 import V3Client

NEW_LINE = "\n" # Python f-strings do not inherently support line breaks via `\n`


def main():

    # Instantiate class objects
    args = get_args()
    v2client = V2Client(args)
    v3client = V3Client(args)

    # Collect group and user data
    group_data = v3client.get_all_user_groups()

    if v2client.soe: # Stack Internal (Enterprise) has email addresses via API v2
        user_data = get_user_data(v2client)
    else: # Stack Internal (Business) or Basic requires email addresses via CSV import
        print("Stack Internal (Business) is not supported yet. Exiting script...")
        raise SystemExit
        # user_data = read_csv(args.users)

    payload_data = process_csv(args.csv, user_data, group_data)
    send_payload_data(payload_data, v3client, args.url)

    print("User groups have been created and/or updated!")


def get_args():

    parser = argparse.ArgumentParser(
        prog='so4t_user_groups.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Uses the Stack Internal API to create/update user groups.',
        epilog = 'Example for Stack Internal (Enterprise): \n'
                'python3 so4t_user_groups.py --url "https://SUBDOMAIN.stackenterprise.co" '
                '--key "YOUR_KEY" --token "YOUR_TOKEN" --csv "users.csv"\n\n')
    
    parser.add_argument('--url', 
                        type=str,
                        help='[Required] Base URL for your Stack Internal instance.')
    parser.add_argument('--key',
                        type=str,
                        help='[Required for Stack Internal (Enterprise)] API key for your Stack '
                        'Internal instance.')
    parser.add_argument('--token',
                        type=str,
                        help='[Required] API token for your Stack Internal instance.')
    parser.add_argument('--csv',
                        type=str,
                        help='[Required] Path to CSV file with users to add to groups.')

    return parser.parse_args()


def read_csv(file_path):

    with open(file_path, 'r') as f:
        csv_data = csv.DictReader(f)
        csv_data = [row for row in csv_data]

    return csv_data


def get_user_data(v2client):

    filter_attributes = [
            "user.email" # email is only available for Stack Internal (Enterprise)
    ]
    filter_string = v2client.create_filter(filter_attributes)

    # Get all users via API
    user_data = v2client.get_all_users(filter_string)

    # Exclude users with an ID of less than 1 (i.e. Community user and user groups)
    user_data = [user for user in user_data if user['user_id'] > 1]

    if 'soedemo' in v2client.api_url: # for internal testing only
        user_data = [user for user in user_data if user['user_id'] > 28000]

    return user_data


def process_csv(file_path, user_data, group_data):

    with open(file_path, 'r') as f:
        csv_data = csv.DictReader(f)
        csv_data = [row for row in csv_data]

    payload_data = {}
    for row in csv_data:
        print(f"Processing row: {row}")
        if not row['group_name_or_id'] or not row['user_email_or_id']:
            print("[WARNING] CSV row is missing either a group name/ID or user email/ID. "
                  "Skipping row...{NEW_LINE}")
            continue

        group_id = convert_string_to_id(
            row['group_name_or_id'], group_data, 'name', 'id')
        user_id = convert_string_to_id(
                row['user_email_or_id'], user_data, 'email', 'user_id')
        
        if not group_id: # `convert_string_to_id` returns `None` if no match is found for group ID
            print(f"[WARNING] Group ({row['group_name_or_id']}) not found in Stack Internal. "
                   "Skipping group...{NEW_LINE}")
            continue
        elif not user_id or type(user_id) == str:
            # `convert_string_to_id` returns `None` if no match is found for user ID
            # `convert_string_to_id` returns the original string if no match is found for email
            print(f"[WARNING] User ({row['user_email_or_id']}) not found in Stack Internal. "
                  "Skipping user...{NEW_LINE}")
            continue
    
        if group_id not in payload_data.keys():
            payload_data[group_id] = []
        payload_data[group_id].append(user_id)

    return payload_data


def send_payload_data(payload_data, v3client, base_url):

    if v3client.soe:
        user_group_url = f"{base_url}/enterprise/user-groups"
    else:
        user_group_url = f"{base_url}/users/groups"

    for group_id, user_ids in payload_data.items():
        if type(group_id) is int: # if group already exists, add new members
            updated_group = v3client.add_users_to_group(group_id, user_ids)
            print(f"Added {len(user_ids)} user(s) to user group '{updated_group['name']}' with ID "
                    f"{updated_group['id']}")
        else: # if group does not exist, create it
            new_group = v3client.create_user_group(group_id, user_ids)
            print(f"Created user group '{new_group['name']}' with ID {new_group['id']} and added "
                    f"{len(user_ids)} user(s) to it")
        print(f"View user group at {user_group_url}/-{updated_group['id']}{NEW_LINE}")


def convert_string_to_id(string, data, search_key, return_key):

    if string.isdigit(): # if string contains only numbers, assume it is an ID
        for item in data: # check if ID exists in data
            if item[return_key] == int(string):
                return int(string)
        return None # if no match is found, return None

    else: # otherwise, search for the string in the data and return the object's ID
        string = string.strip()
        for item in data:
            try:
                if item[search_key].lower() == string.lower():
                    return item[return_key]
            except KeyError: # if the key does not exist, skip it
                return string # if no match is found, return original string
        return string # if no match is found, return None


if __name__ == '__main__':

    main()
