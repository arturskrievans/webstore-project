# webstore-project
A portfolio project demonstrating a full-stack web application using Flask, SQLAlchemy, Socket.IO, and JavaScript.

# How to run it?
1) Install everything via "Download ZIP"
     <br>   or run "git clone https://github.com/arturskrievans/webstore-project.git" in your terminal
2) Go to the installed folder location
3) Run "pip install -r requirements.txt" to install all the dependencies
4) Run "python main.py" to deploy the website

# Website's functionality
A demo webstore that supports user authentication, full CRUD operations, database storage, and basic security protocols. It uses both HTTPS and WebSocket communication for secure and real-time functionality.
<br> Users can start by creating an account, then list or purchase items via the shop.
A user can update information about themselves as well as their listed products. Global chat is also available
once logged in. <br><br>
Database "site.db" has 4 models that store their respective information - User, Product, Purchase & Message. <br>
Passwords are hashed using werkzeug.security library.  <br><br>
site.db already has 1 user commited to it as well as their messages and products. This way you can already see some products in the shop
and pagination in effect. 

<div style="display:flex;flex-direction:row;">
<img width="600" height="412" alt="image" src="https://github.com/user-attachments/assets/16a716ba-2cb9-4a71-8a99-46f393479ec2" />
<img width="190" height="412" alt="image" src="https://github.com/user-attachments/assets/1726fa95-12ca-4f44-bf99-ae0a0d709ae6" />
</div>
<img width="1368" height="860" alt="image" src="https://github.com/user-attachments/assets/5c82b817-9650-43a4-a629-c7dcc98ac611" />
<img width="1355" height="916" alt="image" src="https://github.com/user-attachments/assets/c887f74e-fb26-4883-9f01-ce28788cf5a4" />




# How was the website made?
Backend: Flask, Flask-SocketIO, SQLAlchemy, JavaScript <br>
Frontend: HTML/CSS with JavaScript <br>
WebSockets: Used for real-time chatting implementation<br><br>
<b>This project is designed to demonstrate full-stack development skills, from backend logic to interactive frontend behavior.</b>


