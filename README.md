# Personal Library - Final Project (Lab 10)

This is a Flask-based "Personal Library" web application deployed on Azure App Service. It allows users to create their own accounts and manage a private collection of books.

## Features

-   **User Authentication**: Secure Registration, Login, and Logout functionality.
-   **Private Library**: Each user sees only their own books. Data is isolated per user.
-   **CRUD Operations**: Users can Add, View, Edit, and Delete books.
-   **Azure Blob Storage**: Book cover images are uploaded directly to Azure Blob Storage.
-   **Azure SQL Database**: Persistent storage for user accounts and book metadata.
-   **CI/CD**: Automated deployment via GitHub Actions to Azure App Service.

## Technology Stack

-   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login
-   **Database**: Azure SQL Database (MSSQL)
-   **Storage**: Azure Blob Storage
-   **Frontend**: HTML, Bootstrap 5
-   **Deployment**: Azure App Service (Linux Plan)

## Setup & Installation

### Local Development

1.  Clone the repository:
    ```bash
    git clone <your-repo-url>
    cd <repo-name>
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment variables in a `.env` file:
    ```bash
    AZURE_STORAGE_CONNECTION_STRING="<your-azure-storage-connection-string>"
    # Optional: Connect to Azure SQL locally, or leave blank to use local SQLite
    DB_URL="sqlite:///library.db" 
    SECRET_KEY="your-secret-key"
    ```
4.  Run the application:
    ```bash
    flask run
    ```

### Azure Deployment

1.  **Database**: Follow the instructions in [azure_setup_guide.md](azure_setup_guide.md) to create an Azure SQL Database.
2.  **App Service**: Create a Python Web App on Azure.
3.  **Configuration**: In Azure Portal -> App Service -> Environment Variables, add the following:
    -   `AZURE_STORAGE_CONNECTION_STRING`: Connection string for your Storage Account.
    -   `DB_URL`: Connection string for your Azure SQL Database (see guide).
    -   `SECRET_KEY`: A random string for session security.
    -   `SCM_DO_BUILD_DURING_DEPLOYMENT`: `true`
4.  **Push to GitHub**: The GitHub Actions workflow will automatically build and deploy your app.

## Project Structure

-   `app.py`: Main Flask application logic (Routes, Models, Auth).
-   `storage_helper.py`: Helper function for Azure Blob Storage upload.
-   `templates/`: HTML templates for UI.
-   `.github/workflows`: CI/CD configuration.
-   `azure_setup_guide.md`: Detailed guide for database setup.

## License
MIT
