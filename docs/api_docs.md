# API Documentation

## Authentication
Authentication is handled through token-based mechanisms.

## Endpoints
- **POST /api/authenticate**
    - **Description:** Authenticate a user.
    - **Request Body:**
        - `token` (string): User's authentication token.
    - **Responses:**
        - `200 OK`: Authentication successful.
        - `401 Unauthorized`: Authentication failed.

- **POST /api/consult**
    - **Description:** Process consultation data.
    - **Request Body:**
        - `data` (object): Consultation data.
    - **Responses:**
        - `200 OK`: Consultation processed successfully.

- **POST /api/subscriptions**
    - **Description:** Create a new subscription.
    - **Request Body:**
        - `user_id` (integer): ID of the user.
        - `plan` (string): Subscription plan.
    - **Responses:**
        - `201 Created`: Subscription created successfully.
        - `400 Bad Request`: Invalid input data.
