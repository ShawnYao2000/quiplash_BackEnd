# How to Start Guide

## Quiplash Project Setup

Follow these steps to set up the Quiplash project:

### Prerequisites

- Ensure you have Python installed.
- Ensure you have Node.js and npm installed.
- Install Node Version Manager (nvm) for managing Node.js versions.

### Installation Steps

1. **Navigate to the Quiplash Project Directory:**
   ```
   cd quiplash
   ```

2. **Install Python Dependencies:**
   ```
   pip install -r requirements.txt
   ```

   If `pip` is outdated, upgrade it:
   ```
   python -m pip install --upgrade pip
   ```

3. **Install Azure Functions Core Tools:**

   First, make sure you are using a compatible version of Node.js. Azure Functions Core Tools v3 supports Node.js 14.
   ```
   nvm install 14
   nvm use 14
   ```

   Then, install Azure Functions Core Tools globally:
   ```
   npm install -g azure-functions-core-tools@3 --unsafe-perm true
   ```

   If there are any issues with the Azure Functions Core Tools installation, you may need to update npm to the latest version:
   ```
   npm install -g npm@latest
   ```

4. **Start the Azure Functions Environment:**
   ```
   func start
   ```

   If you encounter a syntax error, ensure you're using the correct version of Node.js and the Azure Functions Core Tools are properly installed.

### Telemetry

Azure Functions Core Tools collects anonymous telemetry data to improve user experience. To opt-out, set the environment variable `FUNCTIONS_CORE_TOOLS_TELEMETRY_OPTOUT` to '1' or 'true'.
