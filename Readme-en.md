# Final Project Topics II - Master's in Software Engineering - UNLP

- This project is a simple application that uses a pre-trained model to calculate similarities between real estate listings.

- Work done by Ariel Moguillansky

# Installation and Setup

1. Clone the repository to your local environment.
2. Ensure that no services are using the ports utilized by the application.
3. Within the root directory of the project, execute `docker-compose up --build`.
4. The client application will run on port 3000.
5. For the first login, enter an email and register at `/register`. Select a subscription type.
6. To use the predictor, assign URIs or entity IDs. To facilitate processing, the number of sent parameters has been limited to 3.
   - Valid URI example: `https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1579031724`
   - Valid ID example: 10000
7. To view the history of requests sent to the intelligent model, visit `/logrequests`.

# Project Architecture

This project implements a microservices architecture for a real estate listing similarity prediction application. It consists of the following services:

* **Webapp:** The main web application that provides the user interface to interact with the system.
* **Registration Service:** Manages user registration, login, and logout functionalities.
* **Prediction Service:** Provides the real estate prediction functionality based on a trained model.
* **Limiter Service:** Implements rate limiting to protect the prediction service from abuse.

## Diagram

![Tp-final](https://github.com/user-attachments/assets/2a5a4329-e2ef-4822-85f7-77cb6f1d3716)

## Components

### 1. Webapp

* **Description:** The web application built with Flask that serves as the user interface.
* **Functionality:**
    * Manages user authentication through the Registration Service.
    * Sends prediction requests to the Prediction Service.
    * Displays prediction results to the user.
    * Manages user sessions using Redis.
    * Displays the requests made by the user.

### 2. Registration Service

* **Description:** Manages user registration and authentication.
* **Functionality:**
    * Registers new users.
    * Authenticates existing users.
    * Manages user sessions using Redis.
    * Logs out users.
    * Maintains the connection with the database for saving users and logs.

### 3. Prediction Service

* **Description:** Uses the pre-trained model to obtain results (scores) from entities (URI or ID) provided by the user.
* **Functionality:**
    * Receives entity requests from the Webapp.
    * Loads and uses a pre-trained machine learning model (`trained_model.pkl`).
    * Queries a knowledge graph to obtain relevant information for prediction.
    * Returns the prediction results to the Webapp.

### 4. Limiter Service

* **Description:** Implements rate limiting to protect the Prediction Service from abuse.
* **Functionality:**
    * Receives requests from the Prediction Service.
    * Verifies if the user has exceeded their request limit.
    * Allows or denies requests based on the rate limit.
    * For Freemium users, the RPM is 5.
    * For Premium users, the RPM is 50.

### 5. MongoDB

* **Description:** Database used to store user information and request logs.
* **Functionality:**
    * Stores user credentials and profile information.
    * Stores request logs for auditing and analysis.

### 6. Redis

* **Description:** In-memory data store used for session management and rate limiting.
* **Functionality:**
    * Stores user session data.
    * Stores request counts for rate limiting.

## Technologies Used

* **Python:** The language used for all services.
* **Flask:** A micro web framework for building the web application and services.
* **MongoDB:** NoSQL database for storing user information and request logs.
* **Redis:** An in-memory data store for session management and rate limiting.
* **Docker:** A containerization platform for packaging and deploying the services.
* **Docker Compose:** A tool for defining and managing multi-container Docker applications.

## Reasoning

The project uses a microservices architecture to achieve the following benefits:

* **Scalability:** Each service can be scaled independently according to its specific needs.
* **Modularity:** Each service is a self-contained unit with a specific responsibility, which facilitates code understanding and maintenance.
* **Technology Diversity:** Each service can use the most appropriate technologies for its specific task.
* **Fault Isolation:** If one service fails, it does not necessarily bring down the entire application.

The use of MongoDB and Redis provides the following benefits:

* **MongoDB:** Provides a flexible and scalable database for storing user information and request logs.
* **Redis:** Provides fast in-memory storage for session management and rate limiting.

The use of Docker and Docker Compose simplifies the deployment and management of the application.

The use of PyKeen allows the Prediction Service to leverage knowledge graph embedding and reasoning for real estate prediction.

# Improvements

This application is merely a test version from which many points for improvement can be extracted.

- Better management of data stored in Redis.
- Implementation of session saving systems (cookie, session storage) for faster queries.
- Improvement in the security and access to user data.
- Implementation of an API gateway as a central entry point for all requests from the web application. A reverse proxy with routing rules can be used.