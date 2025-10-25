# SalesVision XAI-360

A production-ready SaaS product for multimodal explainable AI sales analytics and forecasting.

## 🚀 Features

- **Multimodal Analysis**: Upload sales data (CSV), marketing images, and campaign text
- **Explainable AI**: Get insights from structured data, visual elements, and textual content
- **Time-series Forecasting**: Prophet-powered sales predictions
- **Visual & Textual Insights**: Image metadata analysis and sentiment analysis
- **Subscription Management**: Free, Pro, Business tiers
- **Clean Dashboard**: Modern glass UI with comprehensive insights

## 🛠 Tech Stack

### Frontend
- React + Vite + TailwindCSS
- React Router for navigation
- Recharts for data visualization
- Hosted on Vercel

### Backend
- FastAPI (Python)
- OpenAI API for multimodal insights
- Prophet for forecasting
- SHAP for explainability
- Pillow for image analysis
- Hosted on Hostinger VPS

### Database & Auth
- Supabase (PostgreSQL)
- Supabase Auth
- Stripe for payments

## 📁 Project Structure

```
/salesvision-xai-360
├── frontend/          # React frontend with multimodal UI
├── backend/           # FastAPI backend with multimodal analysis
├── nginx/             # Nginx configuration
├── docker-compose.yml # Full stack deployment
└── README.md          # This file
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Supabase account
- OpenAI API key
- Stripe account

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd salesvision-xai-360
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

3. **Start the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## 🌐 Production Deployment

### Frontend Deployment (Vercel)

1. **Connect your GitHub repository to Vercel**

2. **Set environment variables in Vercel dashboard:**
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_API_URL=https://your-backend-domain.com
   ```

3. **Deploy automatically on git push**

### Backend Deployment (Hostinger VPS)

1. **Set up your VPS**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd salesvision-xai-360
   cp env.example .env
   # Edit .env with production values
   ```

3. **Set up SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

4. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Set up Nginx reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       location / {
           proxy_pass http://localhost:80;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# Backend Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Supabase Setup

1. **Create a new Supabase project**
2. **Run the database migrations:**
   ```sql
   -- Copy the SQL from backend/services/database.py
   -- and run it in your Supabase SQL editor
   ```
3. **Set up authentication providers**
4. **Configure RLS policies**

### Stripe Setup

1. **Create Stripe products and prices**
2. **Set up webhook endpoints**
3. **Configure webhook events:**
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

## 🧠 Multimodal Explainability & AI Narration

SalesVision XAI-360 integrates structured, textual, and visual inputs to provide a holistic, explainable view of sales performance. By analyzing sales numbers, campaign text tone, and ad image properties, the system reveals both data-driven and creative drivers behind business success.

### Input Modalities:
- **📊 Tabular Data**: CSV sales data with numerical analysis
- **💬 Text Analysis**: Marketing campaign descriptions with sentiment analysis
- **🖼️ Visual Analysis**: Ad/product images with metadata extraction

### Output Insights:
- **Combined Analysis**: Integrated insights from all modalities
- **Visual & Textual Insights**: Separate analysis of creative elements
- **Explainable AI**: Clear reasoning behind recommendations

## 🤖 AI Narration System

The dashboard features an intelligent AI narration system that provides real-time insights and explanations:

### AI Insights Panel
- **Collapsible sidebar** with live AI-generated explanations
- **Contextual insights** triggered by chart hover events
- **Historical insight tracking** with timestamped analysis
- **Real-time processing** with animated loading states

### Chart Overlay Annotations
- **Smart callout bubbles** highlighting significant peaks and valleys
- **Animated annotations** with smooth fade-in/out transitions
- **Key metrics display** (sales, sentiment, brightness) in each callout
- **AI-powered insights** explaining performance patterns

### Insight Narration
- **Chart summaries** generated from current dataset analysis
- **Dynamic explanations** that update based on data context
- **Professional narration** with business intelligence focus
- **Real-time updates** reflecting current data state

### Export Functionality
- **PDF report generation** with comprehensive insights
- **Chart summaries** and AI analysis included
- **Professional formatting** for business presentations
- **One-click export** from floating action button

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user

### Multimodal Analysis
- `POST /analyze/` - Upload CSV, image, and text for multimodal analysis
- `POST /forecast/` - Generate sales forecast
- `POST /explain/` - Get AI explanations

### Payments
- `POST /stripe/webhook` - Stripe webhook handler
- `POST /stripe/create-checkout-session` - Create checkout session

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: Built-in Vite health check

### Logs
```bash
# View Docker logs
docker-compose logs -f backend
docker-compose logs -f nginx
```

## 🔒 Security

- JWT token authentication
- CORS configuration
- Input validation
- Rate limiting (recommended)
- HTTPS enforcement
- Secure headers

## 🚀 Scaling

### Horizontal Scaling
- Use load balancer (nginx/HAProxy)
- Multiple backend instances
- Database connection pooling

### Performance Optimization
- Redis for caching
- CDN for static assets
- Database indexing
- API response caching

## 📞 Support

For support, email support@salesvision.ai or create an issue in the repository.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
