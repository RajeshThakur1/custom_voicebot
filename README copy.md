# 🔐 OTP-based Login System

A complete OTP (One-Time Password) based authentication system built with FastAPI and 2factor.in SMS API integration.

## 🌟 Features

- **Phone Number Validation**: Validates Indian mobile number formats
- **OTP Generation**: Generates secure 6-digit numeric OTPs
- **SMS Integration**: Sends OTP via 2factor.in SMS API
- **In-Memory Storage**: Temporary OTP storage with expiration (5 minutes)
- **Rate Limiting**: Maximum 3 attempts per OTP
- **Modern UI**: Beautiful, responsive web interface
- **Real-time Validation**: Client-side and server-side validation
- **Auto-formatting**: Phone number and OTP input formatting

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   2factor.in    │
│   (HTML/JS)     │────│   Backend        │────│   SMS API       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────┐
                       │  In-Memory   │
                       │  OTP Storage │
                       └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- 2factor.in API account and API key
- Indian mobile number for testing

### Installation

1. **Clone or download the project**
   ```bash
   cd "Phone No - OTP"
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # OR
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**
   
   The `API.env` file should contain your 2factor.in API key:
   ```
   API=your_2factor_api_key_here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Open your browser**
   
   Navigate to: http://localhost:8000

### Alternative Setup

You can also use the automated setup script:

```bash
python setup.py
```

## 📱 Usage Flow

1. **Enter Phone Number**: Input your Indian mobile number (+91 format)
2. **Receive OTP**: System sends 6-digit OTP to your phone via SMS
3. **Enter OTP**: Input the received OTP in the verification form
4. **Verification**: System validates the OTP and shows success/failure message

## 🔧 API Endpoints

### Send OTP
```http
POST /send-otp
Content-Type: application/json

{
    "phone": "+919876543210"
}
```

**Response:**
```json
{
    "success": true,
    "message": "OTP sent successfully to +919876543210",
    "phone": "+919876543210"
}
```

### Verify OTP
```http
POST /verify-otp
Content-Type: application/json

{
    "phone": "+919876543210",
    "otp": "123456"
}
```

**Response:**
```json
{
    "success": true,
    "message": "OTP verified successfully",
    "phone": "+919876543210"
}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "message": "OTP service is running"
}
```

## 🛡️ Security Features

- **Phone Number Validation**: Validates Indian mobile number format
- **OTP Expiration**: OTPs expire after 5 minutes
- **Attempt Limiting**: Maximum 3 verification attempts per OTP
- **Input Sanitization**: Removes non-numeric characters from phone/OTP
- **Error Handling**: Comprehensive error handling and user feedback

## 📋 Phone Number Formats Supported

The system accepts various Indian phone number formats:

- `+919876543210`
- `919876543210`
- `09876543210`
- `9876543210`
- `+91 98765 43210`
- `+91-9876-543210`

All formats are normalized to `+919876543210` format internally.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API` | 2factor.in API key | Yes |

### OTP Settings

- **Length**: 6 digits
- **Expiration**: 5 minutes
- **Max Attempts**: 3 per OTP
- **Storage**: In-memory (can be replaced with Redis/Database)

## 🚀 Production Deployment

For production deployment, consider:

1. **Database Storage**: Replace in-memory storage with Redis or database
2. **Environment Variables**: Use proper environment variable management
3. **Rate Limiting**: Implement API rate limiting
4. **Logging**: Add comprehensive logging
5. **HTTPS**: Use HTTPS in production
6. **Error Monitoring**: Implement error tracking
7. **Load Balancing**: Use multiple instances with shared storage

### Production Configuration Example

```python
# Replace in-memory storage with Redis
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def store_otp(phone: str, otp: str):
    redis_client.setex(f"otp:{phone}", 300, otp)  # 5 minutes expiry
```

## 🧪 Testing

### Manual Testing

1. Start the application
2. Open http://localhost:8000
3. Enter a valid Indian mobile number
4. Check your phone for the OTP SMS
5. Enter the received OTP
6. Verify the success message

### API Testing with curl

```bash
# Send OTP
curl -X POST "http://localhost:8000/send-otp" \
     -H "Content-Type: application/json" \
     -d '{"phone": "+919876543210"}'

# Verify OTP
curl -X POST "http://localhost:8000/verify-otp" \
     -H "Content-Type: application/json" \
     -d '{"phone": "+919876543210", "otp": "123456"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **"API key not found"**
   - Check if `API.env` file exists
   - Verify the API key is correctly set

2. **"Failed to send OTP"**
   - Check your 2factor.in account balance
   - Verify the API key is valid
   - Ensure the phone number is in correct format

3. **"Invalid Indian phone number format"**
   - Use a valid Indian mobile number starting with 6, 7, 8, or 9
   - Include country code (+91) if needed

4. **"OTP has expired"**
   - OTPs expire after 5 minutes
   - Request a new OTP

5. **"Maximum OTP attempts exceeded"**
   - You've tried 3 incorrect attempts
   - Request a new OTP

## 📞 Support

For issues related to:
- **2factor.in API**: Contact 2factor.in support
- **Application bugs**: Check the console logs for detailed error messages

## 🔄 Future Enhancements

- [ ] Redis integration for OTP storage
- [ ] Database integration for user management
- [ ] Email OTP option
- [ ] WhatsApp OTP integration
- [ ] Rate limiting middleware
- [ ] Admin dashboard
- [ ] Analytics and reporting
- [ ] Multi-language support

## 📄 License

This project is created for educational purposes. Please ensure compliance with local regulations regarding SMS services and user data handling.
