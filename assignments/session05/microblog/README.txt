Not going to make it to class on Feb 11, so added some extra functionality to the microblog.

- Usernames and passwords are saved to the DB
- Login:
    - username and password must match what is in the DB, otherwise login fails
    - If you attempt to login with a username that does NOT exist in the DB, the user is created (username and password are saved to DB).  Welcome flash message appears.
    - username and password are saved in session, so it is known when a user is still logged into the site
    - if you hit the landing page ('/') but are still logged in, you will be re-directed to /entries.
        - only have this check for the home page.  Security issue if you hit the /entries page directly!
- Logout:
    - username and password are cleared from the session
    - login page is presented upon logout

Appropriate flashes are in place for various actions.
Displaying the usernames and passwords saved in the DB, on the show entries page.

-Nathan Chan
