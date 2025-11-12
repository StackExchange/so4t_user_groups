# Standard Python libraries
import json

# Third-party libraries
import requests


class V3Client(object):

    def __init__(self, args):

        if not args.url: # check if URL is provided; if not, exit
            print("Missing required argument. Please provide a URL.")
            print("See --help for more information")
            raise SystemExit

        if not args.token: # check if API token is provided; if not, exit
            print("Missing required argument. Please provide an API token.")
            print("See --help for more information")
            raise SystemExit
        else:
            self.token = args.token
            #Updated User-Agent
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'User-Agent': 'so4t_user_groups/1.0 (http://your-app-url.com; your-contact@email.com)'
            }

        if "stackoverflowteams.com" in args.url: # Stack Internal (Business) or Basic
            self.team_slug = args.url.split("https://stackoverflowteams.com/c/")[1]
            self.api_url = f"https://api.stackoverflowteams.com/v3/teams/{self.team_slug}"
            self.soe = False
        else: # Stack Internal (Enterprise)
            self.api_url = args.url + "/api/v3"
            self.soe = True

        self.ssl_verify = self.test_connection() # test the API connection

    
    def test_connection(self):

        endpoint = "/tags"
        endpoint_url = self.api_url + endpoint
        ssl_verify = True

        print("Testing API v3 connection...")
        try:
            response = requests.get(endpoint_url, headers=self.headers)
        except requests.exceptions.SSLError:
            print("SSL error. Trying again without SSL verification...")
            response = requests.get(endpoint_url, headers=self.headers, verify=False)
            ssl_verify = False
        
        if response.status_code == 200:
            print("API connection successful")
            return ssl_verify
        else:
            print("Unable to connect to API. Please check your URL and API token.")
            print(response.text)
            raise SystemExit
    

    def get_all_user_groups(self):

        method = "get"
        endpoint = "/user-groups"
        params = {
            'page': 1,
            'pagesize': 100,
        }
        user_groups = self.send_api_call(method, endpoint, params)

        return user_groups


    def create_user_group(self, name, user_ids=[], description=''):
        # `name` is a mandatory field for the API. `description` and `user_ids` are optional.
        
        method = "post"
        endpoint = "/user-groups"
        params = {
            "name": name,
            "description": description,
            "userIds": user_ids
        }
        new_group = self.send_api_call(method, endpoint, params)
        
        return new_group
    

    def edit_user_group(self, group_id, name, description, user_ids):
        # `name` param is required by the API. However, if you don't submit the `description` and 
        # `user_ids` as well, the API treats them as blank submissions, thus deleting anything that
        # might have existed in those fields

        method = "put"
        endpoint = f"/user-groups/{group_id}"
        params = {
            "name": name,
            "description": description,
            "userIds": user_ids
        }
        updated_group = self.send_api_call(method, endpoint, params)

        return updated_group


    def add_users_to_group(self, group_id, user_ids):
        # `user_ids` should be a list of user IDs

        method = "post"
        endpoint = f"/user-groups/{group_id}/members"
        params = user_ids
        response = self.send_api_call(method, endpoint, params)

        if "not found" in response:
            print(f"User group with ID {group_id} not found. Skipping...\n\n")
            return None

        return response


    def send_api_call(self, method, endpoint, params={}):

        get_response = getattr(requests, method, None) # get the method from the requests library
        endpoint_url = self.api_url + endpoint

        data = []
        while True:
            if method == 'get':
                response = get_response(endpoint_url, headers=self.headers, params=params, 
                                        verify=self.ssl_verify)
            else:
                response = get_response(endpoint_url, headers=self.headers, json=params, 
                                        verify=self.ssl_verify)

            # check for rate limiting thresholds
            # print(response.headers) 
            if response.status_code not in [200, 201, 204]:
                print(f"API call to {endpoint_url} failed with status code {response.status_code}")
                print(response.text)
                print(f"Payload data: {params}")
                return response.text
                        
            try:
                json_data = response.json()
            except json.decoder.JSONDecodeError: # some API calls do not return JSON data
                print(f"API request successfully sent to {endpoint_url}")
                return response.text

            if type(params) == dict and params.get('page'): # check request for pagination
                print(f"Received page {params['page']} from {endpoint_url}")
                data += json_data['items']
                if params['page'] == json_data['totalPages']:
                    break
                params['page'] += 1
            else:
                print(f"API request successfully sent to {endpoint_url}")
                return json_data

        return data
