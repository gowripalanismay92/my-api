# Backend API Service (my-api)

## Setup & Run Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Export your Microsoft Entra ID environment variables:
   ```bash
   export TENANT_ID="<your-tenant-id>"
   export API_CLIENT_ID="<your-api-client-id>"
   ```

3. Run the FastAPI server:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```
