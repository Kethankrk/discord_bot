Follow these steps to run this project on your local machine.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python (version specified in the project's requirements)
- pip (Python package installer)

## Step 1: Get the Project Code

First, you need to obtain the project code. You can either:

- Clone the project repository from a version control system like Git.
  ```
  git clone 
  ```
- Download the project code as a ZIP file and extract it.

## Step 2: Create a Virtual Environment (Optional but Recommended)

It's a good practice to create a virtual environment to isolate the project dependencies. Navigate to the project directory and run the following command to create a new virtual environment:

```
python -m venv env
```

## Step 3: Activate the Virtual Environment

Activate the virtual environment:

- On Windows:
  ```
  env\Scripts\activate
  ```

- On Unix or macOS:
  ```
  source env/bin/activate
  ```

## Step 4: Install Project Dependencies

Install the project dependencies by running the following command in the project directory:

```
pip install -r requirements.txt
```

This will install all the required packages listed in the `requirements.txt` file.

## Step 5: Create a .env file

create a .env file to store your discord bot key and add KEY=YOUR_KEY

```
KEY=YOUR_KER
```

## Step 6: Run server

```
python main.py
```
