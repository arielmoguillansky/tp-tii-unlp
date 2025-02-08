# Architectural Improvements

This document outlines potential architectural improvements for the real estate prediction application.

## 1. API Gateway

*   **Description:** Implement an API Gateway as a central entry point for all requests from the Webapp.
*   **Benefits:**
    *   Centralized routing and management.
    *   Authentication and authorization.
    *   Rate limiting.
    *   Request transformation.
*   **Implementation:**
    *   Use a reverse proxy server such as Nginx or HAProxy.
    *   Implement authentication and authorization logic in the API Gateway.
    *   Configure routing rules to forward requests to the appropriate backend services.

## 2. Message Queue

*   **Description:** Use a message queue for asynchronous communication between the Predictor and Limiter services.
*   **Benefits:**
    *   Improved performance.
    *   Increased resilience.
*   **Implementation:**
    *   Use a message queue system such as RabbitMQ or Kafka.
    *   The Predictor Service publishes a message to the queue when it needs to check the rate limit.
    *   The Limiter Service consumes the message from the queue and performs the rate limit check.
    *   The Limiter Service publishes a message to another queue with the result of the rate limit check.
    *   The Predictor Service consumes the message from the queue and proceeds accordingly.

## 3. Service Discovery

*   **Description:** Implement service discovery to allow the services to dynamically locate each other.
*   **Benefits:**
    *   Increased flexibility.
    *   Improved scalability.
*   **Implementation:**
    *   Use a service discovery tool such as Consul or etcd.
    *   Register each service with the service discovery tool.
    *   Use the service discovery tool to locate the other services.

## 4. Backend for Frontend (BFF) per client type
*   **Description**: If there were other clients besides the webapp (e.g. mobile app), a separate BFF could be created tailored to the specific needs of that client.
*   **Benefits**:
    *   Each client receives an API tailored to its specific needs, improving performance and user experience.
    *   Changes to one client's BFF do not affect other clients.
*   **Implementation**:
    *   Create a separate BFF for each client type.
    *   Each BFF aggregates data from the backend services and transforms it to match the needs of the client.
