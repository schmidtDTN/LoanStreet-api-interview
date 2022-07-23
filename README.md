# LoanStreet API Test

- [LoanStreet API Test](#loanstreet-api-test)
  - [Endpoints](#endpoints)
    - [GET /health](#get-health)
    - [POST /db/init](#post-dbinit)
    - [POST /loan](#post-loan)
    - [GET /loans](#get-loans)
    - [GET /loan/{id}](#get-loanid)
    - [PUT /loan/{id}](#put-loanid)
  - [Data Expectations](#data-expectations)

This repository contains my submission for the LoanStreet API coding test. The base web URL for this API is https://loanstreet-api-test.herokuapp.com/api

## Endpoints

### GET /health

The health endpoint is just a simple liveness checker, provided for ease of debugging.
No body is expected, and it should return a 200 if all is well.

### POST /db/init

The database initialization endpoint is provided to reset the database to an out-of-box state. This will drop the **loans** table from the database and recreate it with no data.
No body is expected and it should return a 200 if all goes well.

### POST /loan

The loan creation endpoint allows for the addition of a loan to the database. It expects a JSON body, as detailed in the [Data Expectations](#data-expectations) section.
If a field is not provided, a 400 error will be returned; if an error occurs while writing to the database, a 500 will be returned.
If all goes well, a 200 will be returned, along with a success message containing the newly added loan's ID.

### GET /loans

This endpoint retrieves all loans in the database. If there is an issue retrieving data from the database, a 500 will be returned; if all goes well, a 200 will be returned along with an array of all loans in the database.

### GET /loan/{id}

This endpoint retrieves a single loan from the database by ID, based on the ID passed in by the user in the route. If the requested ID does not exist in the database, a 404 is returned. If an issue occurs while retrieving the data from the database, a 500 will be returned. If all goes well, a 200 will be returned, along with the loan's data in JSON format.

### PUT /loan/{id}

This endpoint allows a user to update an existing loan in the database by ID. The ID is passed in via the route.  
It expects a JSON body, as detailed in the [Data Expectations](#data-expectations) section. Currently, the API does not allow for partial updating of a loan; i.e. all fields must be provided in the request body.
If a field is not provided, a 400 error will be returned; if an error occurs while writing to the database, a 500 will be returned.
If the requested ID does not exist in the database, a 404 is returned. If an issue occurs while retrieving the data from the database, a 500 will be returned.
If all goes well, a 200 is returned, along with a message containing the loan's ID.

## Data Expectations

In order to create or update a loan, a JSON body must be provided. This JSON expects four fields, which must always be provided.

- **amount**: integer
- **rate**: decimal with up to 6 digits total (3 decimal places)
- **length**: integer
- **monthly_payment**: decimal with up to 10 digits total (2 decimal places)
