# Azure SQL Database Setup Guide

This guide will help you create a **permanent** SQL Database on Azure and connect it to your Flask application.

## Prerequisite: Create an Azure SQL Resource

1.  **Log in to Azure Portal**: Go to [portal.azure.com](https://portal.azure.com) and log in with your student account.
2.  **Create a Resource**: Click **"Create a resource"** (top left).
3.  **Search**: Type **"SQL Database"** and select it. Click **"Create"**.

## Step 1: Database Configuration (Basics Tab)

-   **Subscription**: Select "Azure for Students".
-   **Resource Group**: Select your existing resource group (e.g., the one used for your App Service) or create a new one.
-   **Database Name**: Give it a unique name (e.g., `shelf-db-yourname`).
-   **Server**: Click **"Create new"**.
    -   **Server name**: unique name (e.g., `shelf-server-yourname`).
    -   **Location**: Select the same location as your App Service (e.g., `West Europe` or `East US`).
    -   **Authentication method**: Select **"Use SQL authentication"**.
    -   **Server admin login**: Create a username (e.g., `shelfadmin`).
    -   **Password**: Create a STRONG password and **SAVE IT**. You will need this later.
    -   Click **OK**.
-   **Want to use SQL elastic pool?**: No.
-   **Workload environment**: Development.
-   **Compute + storage**: Click **"Configure database"**.
    -   Select **"Service tier"**: **Basic** (Standard or Premium are too expensive).
    -   Data max size: 2 GB (enough for this project).
    -   Click **Apply**.
-   **Backup storage redundancy**: Locally-redundant backup storage.

Click **"Next: Networking"**.

## Step 2: Networking (Firewall Rules)

-   **Connectivity method**: Public endpoint.
-   **Firewall rules**:
    -   **Allow Azure services and resources to access this server**: **YES** (Critical for App Service to connect).
    -   **Add current client IP address**: **YES** (Allows you to connect from your home computer/VS Code).

Click **"Review + create"** -> **"Create"**.
Wait for deployment to finish (approx. 2-5 minutes).

## Step 3: Get Connection String

1.  Go to the newly created **SQL Database** resource.
2.  On the left menu, click **"Connection strings"**.
3.  Copy the string under the **"ADO.NET (SQL authentication)"** tab.
    It looks like this:
    `Server=tcp:shelf-server-yourname.database.windows.net,1433;Initial Catalog=shelf-db-yourname;Persist Security Info=False;User ID=shelfadmin;Password={your_password};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;`

## Step 4: Configure App Service (Environment Variables)

1.  Go to your **App Service** in Azure Portal.
2.  On the left menu, go to **Settings** -> **Environment variables**.
3.  Click **"Add"** (or New Application Setting).
4.  **Name**: `DB_URL`
5.  **Value**: Paste the connection string from Step 3.
    -   **IMPORTANT**: Replace `{your_password}` with the actual password you created in Step 1.
    -   **Note**: For Python/SQLAlchemy compatibility, you must slightly modify the connection string prefix.
    Change `Server=tcp:...` to `mssql+pyodbc://shelfadmin:YOUR_PASSWORD@shelf-server-yourname.database.windows.net/shelf-db-yourname?driver=ODBC+Driver+18+for+SQL+Server`
    
    **Easier Format for `DB_URL` Value:**
    `mssql+pyodbc://<username>:<password>@<server-name>.database.windows.net/<db-name>?driver=ODBC+Driver+18+for+SQL+Server`

6.  Click **Apply** -> **Confirm/Button Save**.
7.  Restart your App Service.

## Step 5: Verify

Your application will now use this permanent Azure SQL database instead of the temporary SQLite file.
The tables will be created automatically (`db.create_all()` in `app.py`) when the app starts.
