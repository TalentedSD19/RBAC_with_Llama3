# Role-Based Access Control and Natural Language to SQL Conversion with Llama 3 

---

#### **Introduction**

This repository contains the source code for a rbaC application designed to convert natural language queries into SQL commands. The application leverages the **LangChain framework** with the **ChatGroq API** and integrates SQL database interactions. It supports user authentication and role-based access control, ensuring secure and structured interactions.

---

### **Features**

1. **Role-Based Access Control (RBAC):**
   - Admin, Moderator, and User roles are supported with specific permissions.
   - Access is granted or denied based on user roles.
   
2. **Natural Language to SQL Conversion:**
   - The chatbot interprets user queries in plain English and generates SQL code to fetch data from the database.

3. **Database Integration:**
   - The application uses SQLite for data storage and manipulation.
   - Includes predefined tables and sample data for users and roles.

4. **Authentication and Authorization:**
   - Secure user login via **JWT (JSON Web Tokens)**.
   - Passwords are securely hashed using **bcrypt**.

5. **Dynamic Karma System:**
   - Tracks user behavior based on access attempts.
   - Grants or deducts "karma" points based on permissions.


---

### **Codebase Overview**

#### **1. File Structure**
- **`bot.py`**: Implements the chatbot using the ChatGroq API for SQL conversion.
- **`main.py`**: Manages the Flask application, routes, and API endpoints.
- **`models.py`**: Handles database operations (creation and query execution).
- **`utils.py`**: Contains utilities such as role-based access control.
- **`config.py`**: Stores configuration variables like database path and secret key.

---

### **Detailed Walkthrough**

#### **1. `bot.py`**
The chatbot uses the **LangChain ChatGroq API** to process English queries and convert them into SQL commands. 

- **Key Components:**
  - **System Message Context:** Provides instructions and schema details for accurate SQL generation.
  - **Few-Shot Examples:** Demonstrates examples of questions and their corresponding SQL responses to improve model performance.
  - **`ask` Function:** Handles user queries and integrates responses into the application flow.

#### **2. `main.py`**
This is the Flask application’s core file. It provides API endpoints for authentication, user operations, and chatbot interactions.

- **Endpoints:**
  - `/register`: Allows user registration with optional role assignment.
  - `/login`: Authenticates users and issues JWT tokens.
  - `/chat`: Processes user queries, generates SQL, executes it, and returns the results (admin/mod-only access).
  - `/admin`, `/mod`, `/user`: Provide role-specific resources and responses.

#### **3. `models.py`**
Manages SQLite database interactions.

- **Functions:**
  - `create_table`: Creates the `user_details` table with predefined columns (e.g., `id`, `role`, `username`, `karma`).
  - `execute_query`: Executes SQL queries with support for fetch, commit, and parameterized inputs.

#### **4. `utils.py`**
Provides helper utilities like role-based access control.

- **`role_required`:**
  - Validates user roles before accessing endpoints.
  - Adjusts user karma based on access behavior (penalizes unauthorized attempts).

#### **5. `config.py`**
Contains essential configuration data:
- `SECRET_KEY`: Used for securing JWT tokens.
- `DATABASE`: Path to the SQLite database file.

---

### **Database Schema**

#### **`user_details` Table**
| Column   | Type      | Attributes                       |
|----------|-----------|----------------------------------|
| `id`     | INTEGER   | Primary Key, Auto Increment      |
| `role`   | INTEGER   | 0=Admin, 1=Moderator, 2=User     |
| `username` | TEXT    | Unique, Not Null                 |
| `password` | TEXT    | Not Null                         |
| `name`   | TEXT      | Optional                         |
| `karma`  | DOUBLE    | Defaults to 0                    |

---

### **Environment Setup**

1. **Prerequisites:**
   - Python 3.9.18
   - SQLite
   - Virtual environment tools (optional but recommended)

2. **Environment Variables:**
   - Create a `.env` file with the following:
     ```
     GROQ_API_KEY=<your_groq_api_key>
     ```

3. **Dependencies:**
   Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Initialization:**
   - Ensure the database file `database.db` is in place.
   - The table `user_details` will be created automatically on the first run.

5. **Run the Application:**
   ```bash
   python main.py
   ```
   The application will be available at `http://127.0.0.1:5000`.

---

### **How It Works**

1. **Registration and Login:**
   - Users can register with a username, password, and name. A role can be optionally assigned during registration.
   - Login authenticates users and provides a JWT token.

2. **Role-Based Queries:**
   - Admin and Moderator roles can access the `/chat` endpoint to process SQL queries via natural language.
   - Unauthorized attempts lead to karma reduction.

3. **Chat Functionality:**
   - The `/chat` endpoint accepts a user query (e.g., *"How many admins are there?"*).
   - Converts it to SQL: `SELECT COUNT(*) FROM user_details WHERE role=0`.
   - Executes the query on the database and returns the results.

---

### **Using the API Endpoints**

This section explains how to interact with the API endpoints provided by the application. All endpoints are designed to ensure security and proper role-based access control (RBAC). Use the `JWT` token for authentication after logging in.

---

### **Base URL**
```
http://127.0.0.1:5000
```

---

### **1. Registration Endpoint**

#### **`POST /register`**
Register a new user.

**Request Body (JSON):**
```json
{
    "username": "john_doe",
    "password": "securepassword123",
    "name": "John Doe",
    "role": 2
}
```
- **Role (Optional):** Defaults to `2` (User). Set `1` for Moderator or `0` for Admin.

**Response:**
- `200 OK`:
  ```json
  {
      "message": "User created successfully"
  }
  ```
- `400 Bad Request`: Missing fields or username already exists.
- `500 Internal Server Error`: Database error.

---

### **2. Login Endpoint**

#### **`POST /login`**
Authenticate the user and get a JWT token.

**Request Body (JSON):**
```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```

**Response:**
- `200 OK`:
  ```json
  {
      "message": "Logged in!",
      "username": "john_doe",
      "name": "John Doe",
      "role": 2,
      "karma": 0,
      "access_token": "<jwt_token>"
  }
  ```
- `400 Bad Request`: Missing username or password.
- `401 Unauthorized`: Invalid credentials.

**Note:**
Use the `access_token` for authentication in subsequent requests by including it in the `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

---

### **3. Chat Endpoint**

#### **`POST /chat`**
Process natural language queries into SQL and execute them. Only accessible by Admins (`role=0`) and Moderators (`role=1`).

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Request Body (JSON):**
```json
{
    "query": "How many admins are there?"
}
```

**Response:**
- `200 OK`:
  ```json
  {
      "current_user": "John Doe",
      "sql_query": "select count(*) from user_details where role=0",
      "response": "The answer for How many admins are there? is :\n\n [(3,)]"
  }
  ```
- `400 Bad Request`: Missing query.
- `403 Forbidden`: Insufficient permissions (karma reduced).
- `404 Not Found`: User not found.

---

### **4. Role-Specific Resource Endpoints**

#### **Admin Resource**

**`GET /admin`**  
Accessible only by Admins (`role=0`).

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response:**
- `200 OK`:
  ```json
  {
      "message": "Welcome to Admin page!",
      "username": "admin_user",
      "name": "Admin",
      "role": 0,
      "karma": 5
  }
  ```

---

#### **Moderator Resource**

**`GET /mod`**  
Accessible by Admins (`role=0`) and Moderators (`role=1`).

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response:**
- `200 OK`:
  ```json
  {
      "message": "Welcome to Moderator page!",
      "username": "mod_user",
      "name": "Moderator",
      "role": 1,
      "karma": 3.5
  }
  ```

---

#### **User Resource**

**`GET /user`**  
Accessible by all authenticated users (Admin, Moderator, or User).

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response:**
- `200 OK`:
  ```json
  {
      "message": "Welcome to User page!",
      "username": "john_doe",
      "name": "John Doe",
      "role": 2,
      "karma": 1.2
  }
  ```

---

### **Error Handling**

- **401 Unauthorized:**
  Occurs if the `JWT` token is missing, expired, or invalid.
- **403 Forbidden:**
  Triggered if the user attempts to access a restricted endpoint without the required role.
- **404 Not Found:**
  Returned if the user is not found in the database.

---


### **Key Notes**

1. **Security:**
   - Passwords are hashed using bcrypt for safe storage.
   - JWT tokens ensure secure communication and user identity.

2. **Scalability:**
   - The modular design allows easy extension of roles, features, and database schema.

3. **Error Handling:**
   - Provides clear messages for missing or invalid input, unauthorized access, and database errors.

---

### **Future Enhancements**

- Add support for additional database operations (e.g., updates, deletes).
- Extend the chatbot to support multi-table queries.
- Integrate role management endpoints for admins.
- Enhance the karma system for community-based incentives.

---

### **Conclusion**

This API provides a seamless interface for managing user roles and performing SQL queries through natural language, ensuring secure access via RBAC and JWT authentication. Use this guide to integrate and test the functionality effectively.
