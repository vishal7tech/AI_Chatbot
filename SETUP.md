# AI Chatbot Part 3 - Setup Guide

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server
- Git

### 1. Clone & Setup Environment
```bash
cd "c:\Users\ACER\OneDrive\Desktop\Project\rule_based_chatbot"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Connect to MySQL and create database
mysql -u root -p
CREATE DATABASE chatbot_db;

# Import sample data (optional)
# The app will automatically create tables
```

### 3. Environment Configuration
Update `.env` file with your database credentials:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=chatbot_db
SECRET_KEY=supersecretkey123
```

### 4. Train the AI Model
```bash
# Option 1: Using Jupyter Notebook (Recommended)
jupyter notebook train_intent_model.ipynb
# Run all cells to train the model

# Option 2: Using Flask Admin Panel
python app.py
# Visit http://localhost:5000/admin
# Click "Train AI Model" button
```

### 5. Run the Application
```bash
python app.py
```

Visit:
- Chat Interface: http://localhost:5000
- Admin Panel: http://localhost:5000/admin
- Chat History: http://localhost:5000/chatlog

## 🔧 Key Features Installed

### Deep Learning Components
- ✅ TensorFlow/Keras neural network
- ✅ TF-IDF vectorization with bigrams
- ✅ Enhanced preprocessing with Indian English stopwords
- ✅ Early stopping and validation
- ✅ Confidence scoring

### Frontend Enhancements
- ✅ Color-coded confidence indicators
- ✅ AI assistant branding
- ✅ Enhanced user experience

### Backend Improvements
- ✅ Multiple responses per intent
- ✅ Random response selection
- ✅ Better error handling
- ✅ Model reload on data changes

## 📊 Model Performance

The trained model includes:
- **Architecture**: 4-layer neural network with dropout
- **Input**: TF-IDF vectors (up to 1000 features)
- **Output**: Intent classification with softmax
- **Training**: Early stopping, validation split
- **Threshold**: 60% confidence for predictions

## 🎯 Usage Examples

Try these messages:
- "hello" / "namaste" / "kya haal hai"
- "fees kitne hain?" / "course price"
- "appointment book karna hai" / "meeting chahiye"
- "thanks" / "dhanyawad" / "shukriya"
- "bye" / "alvida" / "goodbye"

## 🐛 Troubleshooting

### Model Not Found Error
- Train the model first using Jupyter notebook or Admin panel
- Ensure `intent_model.h5`, `vectorizer.pkl`, `label_encoder.pkl` exist

### Database Connection Error
- Check MySQL server is running
- Verify `.env` credentials
- Ensure database `chatbot_db` exists

### Low Accuracy
- Add more diverse patterns per intent
- Ensure at least 5-10 patterns per intent
- Retrain the model after adding data

### Import Errors
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall packages: `pip install -r requirements.txt`

## 📁 File Structure

```
rule_based_chatbot/
├── app.py                 # Main Flask application
├── train_intent_model.ipynb # Jupyter training notebook
├── intent_model.h5        # Trained neural network
├── vectorizer.pkl         # TF-IDF vectorizer
├── label_encoder.pkl      # Intent label encoder
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── templates/
│   ├── chat.html         # Chat interface
│   ├── admin.html        # Admin panel
│   └── chatlog.html      # Chat history
├── static/
│   ├── js/chat.js        # Frontend JavaScript
│   └── css/style.css     # Styles
└── sample_data_fixed.sql # Sample database data
```

## 🔄 Model Retraining

After adding new intents/patterns:
1. Go to Admin Panel
2. Click "Train AI Model"
3. Wait for training completion
4. Model automatically reloads

Or use Jupyter notebook for advanced training options.
