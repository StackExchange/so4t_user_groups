# Stack Internal user groups

Use [so4t_user_groups.html](so4t_user_groups.html) to add users to existing user groups or create new groups from a CSV file. Keep the `assets/` folder beside the HTML file so its bundled Stacks styles load. No Python installation or build step is needed. The page uses **Stack Internal API v3 only**.

The Python scripts are kept for historical reference. They depend on the sunset API v2 and are not the supported way to run this tool.

## What you need

- A Stack Internal Enterprise site and permission to manage user groups.
- An OAuth access token with the API v3 `write_access` scope. Generate one using the [OAuth and PKCE guide](https://support.stackenterprise.co/support/solutions/articles/22000294542-secure-api-token-generation-with-oauth-and-pkce). The account must also be allowed to look up the users in the CSV; API v3 only exposes user email addresses to administrators or the current user.
- A CSV file with these exact columns, in this order:

  ```csv
  user_email_or_id,group_name_or_id
  person1@company.com,Engineering
  28069,1039
  ```

Each row adds one user to one group. Use a user email address or numeric user ID in the first column, and a group name or numeric group ID in the second. A name that does not exist creates a new group. A numeric group ID must already exist. You can download an empty CSV template from the HTML page or use [Templates/users.csv](Templates/users.csv).

## Run the page

1. Open [so4t_user_groups.html](so4t_user_groups.html) in a browser with `assets/` in the same folder.
2. Enter the **site root URL** (for example, `https://your-site.stackenterprise.co`), your OAuth access token, and the CSV file.
3. Select **Review changes**. The page looks up users and groups through API v3 and shows what it will add or create, along with any skipped rows.
4. Select **Apply changes** after reviewing the list. This sends API v3 requests that change group membership and may create groups. If a request fails, the page stops; earlier group changes may already be saved. Run **Review changes** again before retrying.

The token and CSV stay in the browser tab; the page does not save them in browser storage. The browser sends the token and the needed CSV values to your Stack Internal API. Close the tab when finished.

### Browser access to the API

Browser security still controls whether the page can call your Stack Internal site. If you open it as a local `file://` page and the API does not allow that origin, the browser blocks requests. Serve the HTML file and `assets/` folder from the Stack Internal site's origin, or from an origin that your API administrator has allowed for CORS. The API must allow the page's origin, `Authorization` and `Content-Type` headers, and `GET` and `POST` methods. Serving the file from `localhost` alone does not grant access to a different API origin.

If **Review changes** reports that it cannot reach the API, check the URL, network access, token, and the browser's developer console for CORS errors. A successful request from a command-line client does not establish that browser access is allowed.

## Support

Report problems in [GitHub Issues](https://github.com/StackExchange/so4t_user_groups/issues). The tool is provided as-is, without warranty.
