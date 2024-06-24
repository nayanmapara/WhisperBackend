# WhisperBackend
WhisperBackend is a Flask-based backend for web scraping and user subscriptions, hosted on Vercel with MongoDB. It extends Northern Whisper's capabilities, focusing on secure and scalable data management.

## Features
- Web scraping
- User subscription management
- Dashboard for metrics visualization
- API request rate limiting
- Cross-Origin Resource Sharing (CORS) support
- Dockerized deployment

## Prerequisites
- Docker and Docker Compose
- Python 3.7+
- MongoDB
- Vercel account for deployment

## Setup
### Environment Variables
Create a .env file at the root of your project directory with the following content:

```bash
DB_HOST=your_db_host
DB_PASS=your_db_password
DB_NAME=your_db_name
DB_COLLECTION=your_db_collection
```

### Docker Compose
Use Docker Compose to build and run the WhisperBackend service:

```bash
docker-compose up --build
```

## Usage

### API Endpoints

1. **Welcome Endpoint**

   - **GET** `/`
     - Description: Returns a welcome message.

2. **Scrape Links**

   - **GET** `/api/scrape`
     - Description: Scrapes links from a website and returns the results.
     - Rate Limit: 10 requests per month

3. **Subscribe**

   - **POST** `/api/subscribe`
     - Description: Subscribes a user to receive updates.
     - Request Body:
       ```json
       {
         "email": "user@example.com",
         "option": "daily"
       }
       ```

4. **Dashboard**

   - **GET** `/dashboard`
     - Description: Displays metrics visualization for the backend service.

> **Rate Limiting:** The WhisperBackend service uses Flask-Limiter to limit the number of API requests per user. The default rate limit is set to *10 requests per month* by default.

## License
This project is licensed under the Apache License 2.0. See [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for more details.

## Support
For any issues or questions related to WhisperBackend, please [open an issue](https://github.com/nayanmapara/WhisperBackend/issues) on GitHub.

## Contributing
Feel free to open issues or submit pull requests with improvements or bug fixes.