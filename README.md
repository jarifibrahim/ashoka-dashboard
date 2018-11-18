# Ashoka-dashboard

Ashoka dashboard is a team management dashboard built for Ashoka Globalizer. The
dashboard is built using [Django framework](https://www.djangoproject.com/) and [Bootstrap](https://getbootstrap.com/)

![dashboard1](https://user-images.githubusercontent.com/12949454/48671000-ba8fed00-eb47-11e8-9721-c359118df112.png)


**Try it out at - https://ashoka-dashboard-preview.herokuapp.com**. Use username
`testuser` and password `ashokatest`. Note - Some features like (emails and
admin dashboard) are intentionally disabled for the test user.

# Features
1. Automated emails (Reminder and Welcome emails).
2. Team status indicators (Metrics related to team performace).
3. Dynamic forms for feedback and review.


# How to run Locally
1. Clone the project locally using `git clone`.
2. Run `pip install -r requirements.txt` to install all the required packages.
3. Run `python manage.py migrate` to apply migrations to database. By default,
   it uses `SQLite3` database.
4. Run `python manage.py collectstatic` to generate the static files. You don't
   need to run this if `DEBUG=true` flag is set.
5. Run `python manage.py runserver` to start the web server.

Use `DEBUG=true` to enable debug mode
